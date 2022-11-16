
import pygame
from time import time
from math import *
from sprites import *

class Game:
    def __init__(self):
        pygame.init()
        self.players = []
        self.ball = Ball()
        self.ready = False
        self.counter = 3
        self.start = 0
        self.TIMER = 0

    def play(self, pID, data):
        if not self.ready: return
        self.TIMER = floor(time()-self.start)
        if self.TIMER >= 304: self.ready = False
        if self.TIMER <= 3: self.counter = 3-self.TIMER; return
        self.counter = -1
        keys, mouse = data
        if self.players[pID].health > 0:
            self.players[pID].move(keys)
            self.players[pID].ballInteract(self.ball, mouse)
        self.ball.move()

    def beReady(self):
        self.ready = True
        self.start = time()
