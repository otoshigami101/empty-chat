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
                            "id": int(re.sub('.txt', '', filename.split('-')[0]))
                        }).json()

                        chats.append({
                            'id': user['id'],
                            'name': user['name'],
                            'username': user['username'],
                            'status': re.sub('.txt', '', filename.split('-')[1])
                        })

        except Exception as e:
            print('[-] Exception : '+str(e))
            return "[-] failed to get chats"

        return chats

    def setChatStatus(self, dir_name, userId, status):
        try:
            if(status == 'sent' and os.path.exists(self.chat_dir+'/'+dir_name+'/'+userId+'-read.txt')):
                os.rename(self.chat_dir+'/'+dir_name+'/'+userId+'-read.txt',
                          self.chat_dir+'/'+dir_name+'/'+userId+'-sent.txt')
            elif(status == 'read' and os.path.exists(self.chat_dir+'/'+dir_name+'/'+userId+'-sent.txt')):
                os.rename(self.chat_dir+'/'+dir_name+'/'+userId+'-sent.txt',
                          self.chat_dir+'/'+dir_name+'/'+userId+'-read.txt')

        except Exception as e:
            print("[-] error when set read file. exeption : "+str(e))

    def getFileChat(self, dir_name, userId):
        status = 'sent'
        filepath = self.chat_dir+'/'+dir_name+'/'+userId+'-sent.txt'

        if(os.path.exists(filepath) == False):
            filepath = self.chat_dir+'/'+dir_name+'/'+userId+'-read.txt'
            status = 'read'

        return [status, filepath]

    def getChat(self, userId):

        filepath = self.getFileChat(self.uid, userId)[1]
        conversations = []
        try:
            with open(filepath, 'r') as file:
                chat = file.readline().split(',')
                while chat:

                    conversations.append({
                        'time': chat[0],
                        'sender': chat[1],
                        'msg': re.sub(chat[0] + ',' + chat[1] + ',', '', ",".join(chat))
                    })

                    chat = file.readline().split(',')

        except:
            pass

        self.setChatStatus(self.uid, userId, 'read')
        return conversations

    def sendChat(self, receiverId, message):
        if self.initChat(self.uid) & self.initChat(receiverId):
            try:
                timestamp = datetime.today().strftime('%Y-%m-%d %H:%M:%S')

                # write to sender file & receiver id as filename
                filepath = self.getFileChat(self.uid, receiverId)[1]
                with open(filepath, 'a') as f:
                    f.write(
                        timestamp + ','
                        + self.uid + ','
                        + message+'\n'
                    )

                # write to receiver file & sender id as filename
                filepath = self.getFileChat(receiverId, self.uid)[1]
                with open(filepath, 'a') as f:
                    f.write(
                        timestamp + ','
                        + self.uid + ','
                        + message + '\n'
                    )

                self.setChatStatus(receiverId, self.uid, 'sent')
                filepath = self.getFileChat(receiverId, self.uid)[1]
                return "[+] message created."

            except Exception as e:
                print('[-] Exception : '+str(e))

        return "[-] failed to send message"
