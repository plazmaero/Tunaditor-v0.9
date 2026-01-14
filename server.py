import socket
import time
import threading
import pickle
import random

# Kaan: 192.168.13.1
# Adam: 192.168.1.100

class Server:
    def __init__(self, ip="192.168.13.1", port=5000): #LAN 192.168.1.100, WLAN : 192.168.1.8
        self.ip = ip
        
        self.port = port
        self.hub_port = 6000
        self.door_port = 8000
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.thread_count = 0
        self.kill = False
        self.clients = []
        self.creds = {}
        self.valid_tokens = {} #"token": user

    def generate_token(self):
        """Generate a random 3-digit token"""
        return str(random.randint(100, 999))

    def client_listener(self, conn): #this is like client (per client)
        self.thread_count += 1
        obj = {"msg":["yes, kikoemasu!"]}
        while not self.kill:
            try:
                data = conn.recv(1024)
                msg = pickle.loads(data)
                print(f"[RECVED]: {msg}")
                if msg["id"] == "signup":

                    if msg['msg']["user_name"] not in self.creds and msg['msg']["password"] not in self.creds:
                        username = msg['msg']["user_name"]
                        password = msg['msg']["password"]

                        if username not in self.creds:
                            self.creds[username] = password
                            conn.send(pickle.dumps({"msg": "Saved info!", "id": "sign_conf"}))
                            print(self.creds)
                        else:
                            conn.send(pickle.dumps({"msg": "Username already exists!", "id": "sign_conf"}))

                    else:
                        conn.send(pickle.dumps({"msg": "Username already exists!", "id": "sign_conf"}))

            
                        
                        
                if msg["id"] == "login":
                    username = msg["msg"]["user_name"]
                    password = msg["msg"]["password"]

                    if username in self.creds and self.creds[username] == password:
                        token = self.generate_token() #if our cred is right we make a token in server
                        self.valid_tokens[token] = username# assign it
                        conn.send(pickle.dumps({"msg": {"token":str(token), "user": username, "pass": password}, "id": "token_auth"})) #send the token
                        conn.send(pickle.dumps({"msg": "authentication success!", "id": "login_conf"}))
                        #conn.close()
                    else:
                        conn.send(pickle.dumps({"msg": "authentication failed!", "id": "login_conf"}))
                
                #self.handle_token_with_hub(conn,data)
            
            
    
     
            except socket.timeout:
                pass
        
    


            #finally:
                #try:
                    #conn.close()
                
                #except:
                    #pass
                print(f"[SERVER]: CLOSED CONNECTION FOR: {conn}")
        self.thread_count -= 1


    def handle_token_with_hub(self, conn):
        while not self.kill:#new thread
             
        

            try:    
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.connect((self.ip, self.door_port))
                    s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, True)
                    s.settimeout(1)
                    s.send(pickle.dumps({"msg": "connection success", "id": "connect", "from":"SERVER"}))
                    data = s.recv(1024)
                    msg = pickle.loads(data)
                    print(f"[RECVED]: {msg}")
                    
                    if msg["id"] == "token_rev":
                        token = pickle.loads(data)["msg"]
                        print(f"[SERVER] Token verification request from Hub: {token}")

                        if token in self.valid_tokens:
                            username = self.valid_tokens[token]
                            print(f"[SERVER] Token {token} is VALID (belongs to {username})")

                            s.send(pickle.dumps({"msg": "VALID", "id": "token_rev"}))

                        else:

                            print(f"[SERVER] Token {token} is INVALID")
                            s.send(pickle.dumps({"msg": "INVALID", "id": "token_invalid"}))



                
            except:
                pass
       




    def broadcast(self): #this will broadcast one message to all clients in the network
        self.thread_count += 1
        for c in self.clients:
            c.send(pickle.dumps({"msg":["ようこそ！"], "id": "welcome"}))

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
                threading.Thread(target=self.broadcast).start()

                threading.Thread(target=self.client_listener, args=(conn, )).start()
                threading.Thread(target=self.handle_token_with_hub, args=(conn, )).start()
            except socket.timeout:
                continue
            time.sleep(0.01)     


        self.thread_count -= 1

    


    def run(self):
        threading.Thread(target=self.connection_listen).start()


Server().run()
        