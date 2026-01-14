import socket
import threading
import pickle
import time

# Kaan: 192.168.13.1
# Adam: 192.168.1.100

class Portal:
    def __init__(self, ip="192.168.13.1", port=6000): #server port:5555, HUB port: 6000 
        self.ip = ip
        self.port = port
        self.server_port = 5000
        self.door_port = 8000
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.thread_count = 0
        self.kill = False
        self.clients = []
        self.creds = {}
        self.valid_tokens = {} #"token": user
        self.server_com = False


    def verify_token_with_server(self, token):
        """Verify token with the main server"""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((self.ip, self.server_port))
            s.send(pickle.dumps({"msg": token, "id": "token_rev"}))
            response = s.recv(1024).decode()
            #s.close()
            if pickle.loads(response)["id"] == "token_rev":

                return pickle.loads(response)["msg"] == "VALID"
        except:
            return False

    
    def server_listener(self, conn):

        self.thread_count += 1

        while not self.kill:
            try:
                data = conn.recv(1024)
                msg = pickle.loads(data)
                print(f"[RECVED]: {msg}")

                if msg["id"] == "connect" and msg["from"] == "SERVER":
                    self.server_com = True
                    print(f"[STATUS]: SERVER CONNECTION:{self.server_com}")


                
                


                

            except socket.timeout:
                pass

        self.thread_count -= 1

    def client_listener(self, conn):
        self.thread_count += 1

        while not self.kill:
            try:
                data = conn.recv(1024)
                msg = pickle.loads(data)
                print(f"[RECVED]: {msg}")

                


                if msg["id"] == "token_auth": #Client sent message
                    token = msg["msg"]["token"]
                    self.valid_tokens[msg["msg"]["user"]] = token
                    print(self.valid_tokens)

                    #if self.verify_token_with_server(token):

                        #print(f"[HUB] Token {token} verified successfully!")
                        #conn.send(pickle.dumps({"msg":"SUCCESS: Welcome to the Hub! You are now connected.", "id": "token_success"}))
                

            except socket.timeout:
                pass

        self.thread_count -= 1



    def connection_listen(self):
        self.thread_count += 1
        
        self.s.bind((self.ip, self.port))
        while not self.kill:
            self.s.settimeout(1)
            self.s.listen()

            try:
                conn, addr = self.s.accept()
                print(f"[NEW CONNECTION] {conn, addr}")
                self.clients.append(conn)
                #threading.Thread(target=self.broadcast).start()
                if self.clients:

                    threading.Thread(target=self.client_listener, args=(conn, )).start()
                
            except socket.timeout:
                continue
            time.sleep(0.01)     


        self.thread_count -= 1
    
    def server_connection_listen(self):
        self.thread_count += 1
        
        self.s.bind((self.ip, self.door_port))
        while not self.kill:
            self.s.settimeout(1)
            self.s.listen()

            try:
                conn, addr = self.s.accept()
                print(f"[NEW CONNECTION] {conn, addr}")
                self.clients.append(conn)
                #threading.Thread(target=self.broadcast).start()
                if self.clients:

                    threading.Thread(target=self.server_listener, args=(conn, )).start()
                
            except socket.timeout:
                continue
            time.sleep(0.01)     


        self.thread_count -= 1


    


    def run(self):
        threading.Thread(target=self.connection_listen).start()


Portal().run()

        