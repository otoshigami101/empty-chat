#!/usr/bin/env python

import os
from datetime import datetime
import json
import re
import requests


class Chat:

    root_dir = 'chats'
    api_server = 'http://localhost:8081'
    api_headers = {
        "Host": "localhost:8081",
        "Origin": "ws://localhost:4444",
        "X-Requested-With": "XMLHttpRequest",
    }

    def __init__(self, uid):
        self.uid = uid

    def initChat(self, uid):
        try:
            # user id as dir of chat
            if(os.path.isdir(self.root_dir+'/'+uid) == False):
                os.mkdir(self.root_dir+'/'+uid)

            return True
        except Exception as e:
            print("[-] Error when intialize chat : "+str(e))
            return False

    def sendChat(self, receiverId, message):
        if self.initChat(self.uid) & self.initChat(receiverId):
            try:
                timestamp = datetime.today().strftime('%Y%m%d%%H%M%S')

                # write to sender file & receiver id as filename
                with open(self.root_dir+'/'+self.uid+'/'+receiverId+".txt", 'a') as f:
                    f.write('\n'
                            + timestamp + ','
                            + self.uid + ','
                            + message
                            )

                # write to receiver file & sender id as filename
                with open(self.root_dir+'/'+receiverId+'/'+self.uid+".txt", 'a') as f:
                    f.write('\n'
                            + timestamp + ','
                            + self.uid + ','
                            + message
                            )

                return "[+] file created."

            except Exception as e:
                print('[-] Exception : '+str(e))

        return "[-] failed to send message"

    def getChats(self):
        chats = []

        try:
            for root, dirs, files in os.walk(self.root_dir+'/'+self.uid):
                for filename in files:
                    if filename.endswith('.txt'):
                        # get user data from filename as id user
                        user = requests.post(self.api_server+'/user', json={
                            "id": int(re.sub('.txt', '', filename))
                        }, headers=self.api_headers).json()

                        chats.append(
                            {'id': user['id'], 'name': user['name'], 'username': user['username']})

        except Exception as e:
            print('[-] Exception : '+str(e))
            return "[-] failed to get chats"

        return json.dumps({'chats': chats})
