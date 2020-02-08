#!/usr/bin/env python

import os
from datetime import datetime
import json
import re
import requests

class Chat:

    chat_dir = 'chats'
    api_server = 'http://localhost:8081'

    def __init__(self, uid):
        self.uid = uid

    def initChat(self, uid):
        try:
            # user id as dir of chat
            if(os.path.isdir(self.chat_dir+'/'+uid) == False):
                os.mkdir(self.chat_dir+'/'+uid)

            return True
        except Exception as e:
            print("[-] Error when intialize chat : "+str(e))
            return False

    def getChats(self):
        chats = []

        try:
            for root, dirs, files in os.walk(self.chat_dir+'/'+self.uid):
                for filename in files:
                    if filename.endswith('.txt'):
                        # get user data from filename as id user
                        user = requests.post(self.api_server+'/user', json={
                            "id": int(re.sub('.txt', '', filename))
                        }).json()

                        chats.append(
                            {'id': user['id'], 'name': user['name'], 'username': user['username']})

        except Exception as e:
            print('[-] Exception : '+str(e))
            return "[-] failed to get chats"

        return json.dumps({'chats': chats})

    def getChat(self, userId):
        filepath = self.chat_dir+'/'+self.uid+'/'+userId+'.txt'
        conversations = []
        try:
            with open(filepath, 'r') as file:
                chat = file.readline().split(',')
                while chat:

                    conversations.append({
                        'time': chat[0],
                        'sender': chat[1],
                        'msg': re.sub(chat[0] + ',' + chat[1] + ',','',",".join(chat))
                    })

                    chat = file.readline().split(',')

        except:
            pass
        
        return json.dumps({'conversations': conversations})
        
    def sendChat(self, receiverId, message):
        if self.initChat(self.uid) & self.initChat(receiverId):
            try:
                timestamp = datetime.today().strftime('%Y-%m-%d %H:%M:%S')

                # write to sender file & receiver id as filename
                with open(self.chat_dir+'/'+self.uid+'/'+receiverId+".txt", 'a') as f:
                    f.write(
                            timestamp + ','
                            + self.uid + ','
                            + message+'\n'
                            )

                # write to receiver file & sender id as filename
                with open(self.chat_dir+'/'+receiverId+'/'+self.uid+".txt", 'a') as f:
                    f.write(
                            timestamp + ','
                            + self.uid + ','
                            + message + '\n'
                            )

                return "[+] file created."

            except Exception as e:
                print('[-] Exception : '+str(e))

        return "[-] failed to send message"
