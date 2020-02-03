#!/usr/bin/env python
import re
import base64
import json
import struct
from hashlib import sha1
from ChatHandler import Chat


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

        self.lock.acquire()
        try:
            client.send(str(message))
        except:
            print("error sending to a client")

        self.lock.release()

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

                # jwt token for API
                jwt_token = re.search(
                    'jwt_token=(.*?)[\\s]', data).groups()[0].strip()

                self.lock.acquire()
                self.clients[client] = {'jwt_token': jwt_token}
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

                    self.lock.acquire()
                    
                    chat = Chat(self.clients[client]['jwt_token'])
                    if data['request'] == 'chats':
                        print('[+] Request chats from '+str(addr))
                        response = chat.getChats()
                    else:
                        response = "invalid request in received."

                    self.lock.release()

                    self.send_data(client, response)

            except:
                self.lock.acquire()
                del self.clients[client]
                self.lock.release()

        print("[-] Client Closed : "+str(addr))
        client.close()
