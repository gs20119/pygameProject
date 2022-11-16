
import socket
from _thread import *
import sys
from sprites import *
import pickle
from game import Game

########################################################
# Initial Server Setup
########################################################

pygame.init()
host = "192.168.219.108"
port = 5000
CLIENTS, GAMES, SIZE = 0, 0, 6

games = []
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)    # 1. create socket
try: server.bind((host, port))                                # 2. bind host and port to create server
except socket.error as e: print(e)

server.listen(2)                                              # 3. server listens for any client
print("Wating for a connection, Server Started")

########################################################
# Start Thread when Connected
########################################################

def clientThread(connection, pID, rID):                    # Inside thread
    game = games[rID]
    game.players.append(Player(pID))
    connection.sendall(pickle.dumps(pID))                  # send initial info to client
    while True:                                               # 6. repeat sending and recieving on thread
        try:
            data = pickle.loads(connection.recv(2048))
            game.play(pID,data)
            connection.sendall(pickle.dumps(game))
        except Exception as e: print(e); break
    print("Disconnected")
    game.players[pID].online = False
    connection.close()                                        # 7. close connection after used


while True:
    connection, address = server.accept()                              # 4. server accepts a new connection
    print("Connected to: ", address)
    RoomID, PlayerID = CLIENTS // SIZE, CLIENTS % SIZE
    CLIENTS += 1
    if CLIENTS % SIZE == 1: games.append(Game())
    if CLIENTS % SIZE == 0: games[RoomID].beReady()
    start_new_thread(clientThread, (connection, PlayerID, RoomID))     # 5. starts new thread for this


########################################################


