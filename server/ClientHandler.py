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
    client_allowed = {"http://localhost:8080", "http://192.168.43.179:8080"}
    clients = {}

    def __init__(self, LOCK):
        self.lock = LOCK

    def recv_data(self, client):
        # Turn string values into opererable numeric byte values
        stringStreamIn = client.recv(9999)
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

        # Loop through each byte that was received
        self.lock.acquire()
        while i < len(byteArray):

            # Unmask this byte and add to the decoded buffer
            decodedChars += chr(byteArray[i] ^ masks[j % 4])
            i += 1
            j += 1

        self.lock.release()
        # Return the decoded string
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

    def setConnectedStat(self, uid, status):
        for conn_client in self.clients:
            chat = Chat(self.clients[conn_client]['uid'])
            if self.clients[conn_client]['current_conversation'] == uid:
                msg = json.dumps({
                    'chat': chat.getChat(uid),
                    'isConnected': status
                })
                self.lock.acquire()
                self.send_data(conn_client, msg)
                self.lock.release()
            
            
            resp = json.dumps({
                'users' : chat.getUsers(self.clients)
            })

            self.lock.acquire()
            self.send_data(conn_client, resp)
            self.lock.release()

    def getConnectedStat(self, uid):
        status = False
        for conn_client in self.clients:
            if self.clients[conn_client]['uid'] == uid:
                status = True
                break
        
        return status

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
                self.clients[client] = {'uid': uid, 'current_conversation': ''}
                self.lock.release()

                return True
        else:
            print('[-] Unknown Origin Header')
            return False

    def handler(self, client, addr):
        if(self.handShake(client)):
            try:
                self.setConnectedStat(self.clients[client]['uid'], True)
                while 1:

                    recv = self.recv_data(client)
                    data = json.loads(recv)
                    chat = Chat(self.clients[client]['uid'])

                    self.lock.acquire()
                    if data['request'] == 'chats':
                        print('[+] Request chats from '+str(addr))
                        response = json.dumps({
                            'chats': chat.getChats()
                        })

                    elif data['request'] == 'users':
                        print('[+] Request users from '+str(addr))
                        response = json.dumps({
                            'users' : chat.getUsers(self.clients)
                        })
                        
                    elif data['request'] == 'conversations':
                        print('[+] Request conversations from '+str(addr))
                        if data['userId']:
                            response = json.dumps({
                                'chat': chat.getChat(data['userId']),
                                'isConnected': self.getConnectedStat(data['userId'])
                            })
                            self.clients[client]['current_conversation'] = data['userId']
                        else:
                            response = json.dumps(
                                {"errors": "Invalid Request"})

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

                                # refresh conversation and chats for sender
                                conversation = json.dumps({
                                    'chat': chat.getChat(receiver_id),
                                    'isConnected': self.getConnectedStat(receiver_id)
                                })
                                self.lock.acquire()
                                self.send_data(client, conversation)
                                self.lock.release()

                                chats = json.dumps({
                                    'chats': chat.getChats()
                                })
                                self.lock.acquire()
                                self.send_data(client, chats)
                                self.lock.release()

                                for client_receiver in self.clients:
                                    if(self.clients[client_receiver]['uid'] == receiver_id):
                                        chat = Chat(receiver_id)
                                        if(self.clients[client_receiver]['current_conversation'] == sender_id):
                                            # refresh conversation for receiver
                                            conversation = json.dumps({
                                                'chat': chat.getChat(sender_id),
                                                'isConnected': self.getConnectedStat(sender_id)
                                            })
                                            self.lock.acquire()
                                            self.send_data(
                                                client_receiver, conversation)
                                            self.lock.release()
                                        else:
                                            #send new msg notif for receiver
                                            user = chat.getUser(receiver_id)
                                            newMsg = json.dumps({
                                                'newMsg' : {
                                                    'id': sender_id,
                                                    'username': user['username'],
                                                    'msg': data['message']
                                                }     
                                            })
                                            self.lock.acquire()
                                            self.send_data(client_receiver,newMsg)
                                            self.lock.release()

                                        # refresh chats for receiver
                                        chats = json.dumps({
                                            'chats': chat.getChats()
                                        })
                                        self.lock.acquire()
                                        self.send_data(client_receiver, chats)
                                        self.lock.release()

                                        break

                                print(
                                    "[+] Chat & Conversation Refreshed. \n\n\n")
                                continue

                            else:
                                response = json.dumps(
                                    {"errors": "Failed to send chat."})
                        else:
                            response = json.dumps(
                                {"errors": "Invalid Request"})
                    
                    else:
                        response = json.dumps({"errors": "Invalid Request"})
                    self.lock.release()
               
                    self.send_data(client, response)

            except Exception as e:
                print("[-] Exception : "+str(e))
                uid = self.clients[client]['uid']
                self.lock.acquire()
                del self.clients[client]
                self.lock.release()
                self.setConnectedStat(uid, False) 

        print("[-] Client Closed : "+str(addr))
        client.close()
