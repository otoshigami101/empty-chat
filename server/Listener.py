#!/usr/bin/env python

import socket, threading
from ClientHandler import Client

class Listener:

    LOCK = threading.Lock()

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.client = Client(self.LOCK)

    def start(self):
        s = socket.socket()
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((self.host, self.port))
        s.listen(0)

        print("==== Server Started. ====")
        
        while 1:
            conn, addr = s.accept()
            print("\n\n==== Got a Connection from "+str(addr)+" ====")
            threading.Thread(target=self.client.handler, args=( conn , addr)).start()


listener = Listener('127.0.0.1', 4444)
listener.start()
