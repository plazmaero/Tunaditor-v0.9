import socket
import pickle
import struct

class Network:
    def __init__(self, mode):
        self.IP = ""
        self.PORT = ""
        self.FACTOR = 2
        self.BUFFER = 1024 * self.FACTOR
        self.mode = mode
        self.packet = {"MESSAGE": "", "SUCCESS": False, "TYPE": ""}        
        self.temporary_packet = {}
    def send_string(self, comms, data=""):
        comms.send(data.encode("utf-8"))

#A wait I know fix    
    def recv_string(self, comms):
        data = comms.recv(self.BUFFER).decode("utf-8")
        return data

    #def send_obj(self, comms, data):
     #  encoded_obj = pickle.dumps(data)
      # comms.sendall(struct.pack("!I", len(encoded_obj)))  # Send the length first
       #comms.sendall(encoded_obj)  # Send the actual data


#imposible even

#I think I deleted the original send

#it should work now man shh
    def send_obj(self, comms, data):
       encoded_obj = pickle.dumps(data)
       comms.send(encoded_obj)

    def send_obj_stream(self, comms, data):
        encoded_obj = pickle.dumps(data)
        comms.sendall(encoded_obj)

    def send_data_stream(self, comms, data, type):
#i just removed the STRING if statment ik it doesn't make sense since everything we send is just object but keep it this for now I will remove during optmization        
        if type == "OBJECT":
            encoded_obj = pickle.dumps(data) #bro stop let's playtest
            comms.sendall(encoded_obj)

    def warn(self, comms, data):
        self.send_string(comms, data)

    def recv_obj(self, comms):
        decoded_obj = pickle.loads(comms.recv(self.BUFFER))
        return decoded_obj    

    def send_data(self,comms, data, type):
        
        if type == "OBJECT":
            self.send_obj(comms, data)
    

    def recv_data(self, comms, channel_type): #if you want to recv string do this, output_string = recv_data(comms, "STRING")
        #print(f"channel_type {channel_type}")
        
        
        #print(f"channel_type {warn_sign}")
#let's playtest now
        output = None
    
        #if warn_sign == "OBJECT": # when you want to send data do this send_data(self, comms, {wtvr}, "OBJECT")
        output = self.recv_obj(comms)#if you want to send string do this send_data(self, comms, "wtvr", "STRING")

        print(f"recieved data {output}")
        return output


    def connect(self, comms):
        try:
            return self.recv_string(comms)
        except:
            print("Connection Failed")
    
