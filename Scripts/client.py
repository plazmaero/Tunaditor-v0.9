# client.py
import socket, threading, pickle, time
import queue

# Kaan: 192.168.13.1
# Adam: 192.168.1.100

class Client:
    def __init__(self, ip="192.168.13.1", port=5000):
        self.ip = ip
        self.port = port
        self.hub_port = 6000
        self.kill = False
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.share = ""
        self.user_data = {"user":"", "pass":""}
        self.queue = queue.Queue()
        self.online = True
        self.logged = False
        self.token = None
        
    def run_listen(self):
        #s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((self.ip, self.port))
        self.s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, True)
        self.s.settimeout(1)
     
        while not self.kill:
            try:
                data = self.s.recv(1024)
                if not data:
                    continue
                msg = pickle.loads(data) #I forgot something
                print(msg)
                if msg["id"] == "token_auth":
                    self.token = msg["msg"]["token"]
                    self.user_data["user"] = msg["msg"]["user"]
                    self.user_data["pass"] = msg["msg"]["pass"]
                    
                    
                    
                self.queue.put(msg)
                

                #self.share = msg
                #if msg["id"] == "login_token" and not self.user_data["user"]:
                    #self.user_data["user"] = msg["msg"]["user"]
                    #self.user_data["pass"] = msg["msg"]["pass"]
                    #print("✅ user_data updated:", self.user_data)
                
                time.sleep(0.1)
            except socket.timeout:
                pass
        
        #self.connect_hub()
    

    def connect_hub(self):
        print("Waiting for token...")
        while self.token is None and not self.kill:

            time.sleep(0.1)

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        s.connect((self.ip, self.hub_port))
        s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, True)
        s.settimeout(1)
        
        print("SENDING TOKEN")
        s.send(pickle.dumps({"msg": {"token":self.token, "user":self.user_data["user"]}, "id": "token_auth"}))
        while not self.kill:
            try:
                data = s.recv(1024)

                    
                msg = pickle.loads(data) #I forgot something
                print(msg)
                    
                #print("SENDING TOKEN")
                #s.send(pickle.dumps({"msg": self.token, "id": "token_auth"}))
                self.queue.put(msg)

                    #self.share = msg
                    #if msg["id"] == "login_token" and not self.user_data["user"]:
                        #self.user_data["user"] = msg["msg"]["user"]
                        #self.user_data["pass"] = msg["msg"]["pass"]
                        #print("✅ user_data updated:", self.user_data)
                time.sleep(0.1)
            except socket.timeout:
                pass
     
        
            


#
# singleton instance
client_instance = Client()
 