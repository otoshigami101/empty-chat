#!/usr/bin/env python
import re
import base64
import json
import struct
from hashlib import sha1
from ChatHandler import Chat
import requests


class Client:
    websocket_answer = (
        'HTTP/1.1 101 Switching Protocols',
        'Upgrade: websocket',
        'Connection: Upgrade',
        'Sec-WebSocket-Accept: {key}\r\n\r\n',
    )
    client_allowed = {"http://localhost:8080", "http://localhost:8082"}
    clients = {}

    def __init__(self, LOCK):
        self.lock = LOCK

    def recv_data(self, client):
        # Turn string values into opererable numeric byte values
        stringStreamIn = client.recv(4096)
        byteArray = [ord(character) for character in stringStreamIn]
        datalength = byteArray[1] & 127
        indexFirstMask = 2

        if datalength == 126:
            indexFirstMask = 4
        elif datalength == 127:
            indexFirstMask = 10

        # Extract masks
        masks = [m for m in byteArray[indexFirstMask: indexFirstMask+4]]
        indexFirstDataByte = indexFirstMask + 4

        # List of decoded characters
        decodedChars = ''
        i = indexFirstDataByte
        j = 0

        self.lock.acquire()
        # Loop through each byte that was received
        while i < len(byteArray):

            # Unmask this byte and add to the decoded buffer
            decodedChars += chr(byteArray[i] ^ masks[j % 4])
            i += 1
            j += 1

        # Return the decoded string
        self.lock.release()

        return decodedChars

    def send_data(self, client, data):
        """
        Encode and send a WebSocket message
        """
        s = data

        # Empty message to start with
        message = ""

        # always send an entire message as one frame (fin)
        b1 = 0x80

        # in Python 2, strs are bytes and unicodes are strings
        if type(s) == unicode:
            b1 |= 0x01
            payload = s.encode("UTF8")

        elif type(s) == str:
            b1 |= 0x01
            payload = s

        # Append 'FIN' flag to the message
        message += chr(b1)

        # never mask frames from the server to the client
        b2 = 0

        # How long is our payload?
        length = len(payload)
        if length < 126:
            b2 |= length
            message += chr(b2)

        elif length < (2 ** 16) - 1:
            b2 |= 126
            message += chr(b2)
            l = struct.pack(">H", length)
            message += l

        else:
            l = struct.pack(">Q", length)
            b2 |= 127
            message += chr(b2)
            message += l

        # Append payload to message
        message += payload
        try:
            client.send(str(message))
        except:
            print("error sending to a client")

    def chat_broadcast(self):
        for client in self.clients:
            try:
                # broadcast chat
                chat = Chat(self.clients[client]['uid'])
                chats = chat.getChats()
                self.send_data(client, chats)
            except Exception as e:
                print("[-] Failed to send chat broadcast : "+str(e))

    def handShake(self, client):
        data = client.recv(4096)

        print("[+] Header : \n"+str(data))

        if "Origin" in data:
            origin = re.search(
                'Origin:\\s+(.*?)[\n\r]', data).groups()[0].strip()
            if origin not in self.client_allowed:
                print('[-] Not Allowed Origin Header From : '+origin)
                return False
            else:
                secKey = re.search(
                    'Sec-WebSocket-Key:\\s+(.*?)[\n\r]', data).groups()[0].strip()
                respKey = base64.b64encode(
                    sha1(secKey + "258EAFA5-E914-47DA-95CA-C5AB0DC85B11").digest())

                answer = '\r\n'.join(self.websocket_answer).format(key=respKey)
                print("[+] Sending Response : \n"+answer)

                client.send(answer)
                print("[+] Response Sent.")

                # get user id
                uid = re.search(
                    'uid=(.*?)[\\s]', data).groups()[0].strip()

                self.lock.acquire()
                self.clients[client] = {'uid': uid}
                self.lock.release()

                return True
        else:
            print('[-] Unknown Origin Header')
            return False

    def handler(self, client, addr):
        if(self.handShake(client)):
            try:
                while 1:
                    data = json.loads(self.recv_data(client))
                    chat = Chat(self.clients[client]['uid'])

                    self.lock.acquire()

                    if data['request'] == 'chats':
                        print('[+] Request chats from '+str(addr))
                        response = chat.getChats()
                    elif data['request'] == 'conversations':
                        print('[+] Request conversations from '+str(addr))
                        if data['userId']:
                            response = chat.getChat(data['userId'])
                        else:
                            response = json.dumps({ "errors" : "Invalid Request"})

                    elif data['request'] == 'send_chat':
                        if data['userId'] and data['message']:
                            print('[+] Receive chat from '+str(addr))
                            response = chat.sendChat(
                                data['userId'], data['message'])

                            if "failed" not in response:
                                self.lock.release()
                                
                                print('[+] Refreshing chat & conversation')
                                sender_id = self.clients[client]['uid']
                                receiver_id = data['userId']
                                
                                #refresh chat and conversation for sender
                                chats = chat.getChats()
                                self.lock.acquire()
                                self.send_data(client, chats)
                                self.lock.release()

                                conversation = chat.getChat(receiver_id)
                                self.lock.acquire()
                                self.send_data(client, conversation)
                                self.lock.release()
                                
                                self.lock.acquire()
                                for client_receiver in self.clients:
                                    if(self.clients[client_receiver]['uid'] == receiver_id):
                                        self.lock.release()
                                        chat = Chat(receiver_id)
                                        
                                        #refresh chat and conversation for receiver
                                        chats = chat.getChats()
                                        
                                        self.lock.acquire()
                                        self.send_data(client_receiver, chats)
                                        self.lock.release()
                                        
                                        conversation = chat.getChat(sender_id)
                                        
                                        self.lock.acquire()
                                        self.send_data(client_receiver, conversation)
                                        self.lock.release()
                            
                                print("[+] Chat & Conversation Refreshed. \n\n\n")
                                continue

                            else:
                                response = json.dumps({ "errors" : "Failed to send chat."})    
                        else:
                            response = json.dumps({ "errors" : "Invalid Request"})
                    else:
                        response = json.dumps({ "errors" : "Invalid Request"})

                    self.lock.release()

                    self.lock.acquire()
                    self.send_data(client, response)
                    self.lock.release()

            except Exception as e:
                print("[-] Exception : "+str(e))
                self.lock.acquire()
                del self.clients[client]
                self.lock.release()

        print("[-] Client Closed : "+str(addr))
        client.close()
