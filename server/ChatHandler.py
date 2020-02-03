import requests
import os
import fnmatch
from datetime import datetime


class Chat:

    api = 'http://localhost:8081'
    chat_dir = '/chats'

    def __init__(self, jwt_token):
        self.jwt_token = jwt_token
        self.initUser()

    def initUser(self):
        try:
            r = requests.post(self.api+'/validate_login', json={
                "jwt_token": self.jwt_token
            }).json()
            self.user = r['data']

        except Exception as e:
            print("[+] Error when intialize user : "+str(e))

    def sendChat(self, userId, message):

        timestamp = datetime.today().strftime('%Y%m%d%%H%M%S')
        # write to sender file
        with open(self.chat_dir+"/"+self.user['id'], 'a') as f:
            f.write('\n'
                    + timestamp + ','
                    + self.user['id'] + ','
                    + message
                    )

            print(f.read())

        # write to receiver file & make receiver id as filename
        with open(self.chat_dir+"/"+userId, 'a') as f:
            f.write('\n'
                    + timestamp + ','
                    + self.user['id'] + ','
                    + message
                    )
            
            print(f.read())
        


    def getChats(self):        

        if(os.path.exists(self.chat_dir+"/"+self.user['id'])):
            response = fnmatch.filter(os.listdir(
            self.chat_dir+"/"+self.user['id']), '*.txt')
        else:
            response = 'Chat Not Found.'


        return response
