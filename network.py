
import socket
import pickle

###############################################################

class Network:
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = "192.168.219.108"
        self.port = 5000
        self.address = (self.host, self.port)              # address of the server (destination)
        self.playerID = self.connect()

    def getID(self):
        return self.playerID

    def connect(self):
        try:
            self.client.connect(self.address)              # client connects to server while listening
            return pickle.loads(self.client.recv(2048))    # recieve pickled data which sent from server
        except Exception as e: print(e)

    def send(self, *data):
        try:
            self.client.send(pickle.dumps(data))           # pickle any data and send to the server
            return pickle.loads(self.client.recv(2048))    # recieve pickle data which sent from server
        except Exception as e: print(e)

###############################################################
