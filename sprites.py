
import pygame
from math import *
from time import time

##############################################################
# Sprites (Components of the game)                           #
##############################################################

initPos = [
    (-100,0), (100,0),
    (-50,-50*sqrt(3)), (50,-50*sqrt(3)),
    (-50,50*sqrt(3)), (50,50*sqrt(3)),
]
teamR, teamB = 0, 1
RED = (200,50,50)
BLUE = (50,50,200)
GREEN = (50,200,50)
WHITE = (240,240,240)
BLACK = (0,0,0)
RADIUS = 25
ballRADIUS = 15
VMAX = 4
sVMAX = 2
GRAVITY = 0.01

def HEXAGON(k, X, Y, WIDE):
    return [
        (-50*k+X-25*WIDE, -50*sqrt(3)*k+Y), (50*k+X+25*WIDE, -50*sqrt(3)*k+Y),
        (100*k+X+25*WIDE, Y), (50*k+X+25*WIDE, 50*sqrt(3)*k+Y),
        (-50*k+X-25*WIDE, 50*sqrt(3)*k+Y), (-100*k+X-25*WIDE, Y)
    ]


##############################################################
# Sprites (Components of the game)                           #
##############################################################

class Player(pygame.sprite.Sprite):
    def __init__(self, pID):
        self.ID = pID
        self.x, self.y = initPos[pID]
        self.r = RADIUS
        self.vx, self.vy = 0, 0
        self.z, self.Z, self.vz = 0, 40, 0
        self.team = pID % 2
        self.color = RED if self.team == teamR else BLUE
        self.jumpReady = True
        self.myself = False
        self.online = True
        self.sit = False
        self.center = 0, 0
        self.hold = None
        self.clickReady = True
        self.clickTime = 0
        self.clickAdmit = True
        self.throwing = False
        self.throwAngle = 0 # -2, -1, 0, 1, 2
        self.throwTime = 0
        self.throwPower = 0
        self.health = 3
        self.kills = 0

    def draw(self, win):
        if self.health == 0: return
        self.center = win.get_width()/2, win.get_height()/2
        X = self.x + self.center[0]
        Y = self.y + self.center[1]
        if self.myself:
            pygame.draw.circle(win, GREEN, (X,Y), self.r+4)
        pygame.draw.circle(win, self.color, (X,Y), self.r)
        for i in range(self.health):
            m, n = i//3, i%3
            rect = pygame.Rect(X-12+10*n, Y+self.r+5+5*m, 5, 5)
            pygame.draw.rect(win, (150,100,150), rect)
        colour_rect = pygame.Surface((2,2))                                   # tiny! 2x2 bitmap
        pygame.draw.line(colour_rect,(min(250,50+3*self.z),200,min(250,300-3*self.z)), (0,1),(1,1))            # left colour line
        pygame.draw.line(colour_rect,(min(250,50+3*self.Z),200,min(250,300-3*self.Z)),(0,0),(1,0))            # right colour line
        colour_rect = pygame.transform.smoothscale(colour_rect,(7,40))  # stretch!
        win.blit(colour_rect, pygame.Rect(X-35,Y-20,5,50))

    def move(self, keys):
        if keys[pygame.K_SPACE] and self.z == 0 and self.jumpReady:
            self.jumpReady = False; self.vz = 1.5
        if not keys[pygame.K_SPACE]: self.jumpReady = True

        self.sit = keys[pygame.K_LSHIFT] and self.z == 0
        self.Z = self.z+40; V = VMAX
        if self.sit: self.Z = self.z+20; V = sVMAX
        V = sVMAX if self.sit else VMAX

        if keys[pygame.K_1]: self.throwAngle = -1
        elif keys[pygame.K_2]: self.throwAngle = 0
        elif keys[pygame.K_3]: self.throwAngle = 1

        if keys[pygame.K_a]: self.vx = min(0,max(self.vx-0.5, -V))
        elif keys[pygame.K_d]: self.vx = max(0,min(self.vx+0.5, V))
        else: self.vx = 0

        if keys[pygame.K_w]: self.vy = min(0,max(self.vy-0.5,-V))
        elif keys[pygame.K_s]: self.vy = max(0,min(self.vy+0.5,V))
        else: self.vy = 0

        self.vz -= 3*GRAVITY
        if self.z == 0: self.vz = max(0,self.vz)

        self.x += self.vx
        self.y += self.vy
        self.z = max(0,self.z+self.vz)

        if self.team == teamR: self.CHECK_RED(3.5,2)
        else: self.CHECK_BLUE(3.5,2)


    def ballInteract(self, ball, mouse):
        click, pos = mouse
        if not click[0]:
            self.clickReady = True
            self.clickAdmit = True
        if ball.hold and self.hold is not ball: return
        if self.hold is None:
            if self.z <= ball.z <= self.Z:
                dist = sqrt(pow(self.x-ball.x,2)+pow(self.y-ball.y,2))
                if ball.thrown is None or (ball.thrown.team == self.team):
                    if click[0] and self.clickAdmit and dist <= (self.r+ball.r)+5:
                        self.hold = ball
                        ball.hold = True
                elif (ball.r+self.r) < dist < (ball.r+self.r)+30:
                    if (click[0] and self.clickAdmit):
                        self.hold = ball
                        ball.hold = True
                elif dist < (ball.r+self.r):
                    self.health -= 1
                    ball.thrown.kills += 1
                    if ball.thrown.kills % 2 == 0:
                        ball.thrown.health += 1
                    self.hold = ball
                    ball.hold = True

        else:
            if click[0] and self.clickReady:
                self.throwing = True
                self.throwTime = time()
            elif self.throwing:
                if click[0]:
                    self.throwPower = min(2,int(time()-self.throwTime))
                    print(self.throwPower)
                else:
                    dist = sqrt(pow(self.x-pos[0],2)+pow(self.y-pos[1],2))
                    dir = ((pos[0]-self.x)/dist, (pos[1]-self.y)/dist)
                    ball.x, ball.y, ball.z = self.x, self.y, self.Z
                    ball.vx = (2.5+0.5*self.throwPower)*dir[0]*cos(pi*self.throwAngle/12)
                    ball.vy = (2.5+0.5*self.throwPower)*dir[1]*cos(pi*self.throwAngle/12)
                    ball.vz = (2.5+0.5*self.throwPower)*sin(pi*self.throwAngle/12)*0.4
                    ball.hold = False
                    ball.thrown = self
                    self.hold = None
                    self.throwing = False
        if click[0]:
            if self.clickReady:
                self.clickReady = False
                self.clickTime = time()
            elif time()-self.clickTime > 0.5:
                self.clickAdmit = False


    def CHECK_RED(self,k,WIDE):
        X, Y = self.center
        self.x = min(X,self.x)
        self.y = max(-50*sqrt(3)*k+Y,min(50*sqrt(3)*k+Y,self.y))
        AC = self.x+100*k-X+25*WIDE, self.y-Y
        if self.y+sqrt(3)*self.x < Y+sqrt(3)*(-100*k+X-25*WIDE):
            ABAC = (AC[0]-AC[1]*sqrt(3))/2
            self.x = (-100*k+X-25*WIDE) + ABAC*1/2
            self.y = (Y) - ABAC*sqrt(3)/2
        if self.y-sqrt(3)*self.x > Y-sqrt(3)*(-100*k+X-25*WIDE):
            ABAC = (AC[0]+AC[1]*sqrt(3))/2
            self.x = (-100*k+X-25*WIDE) + ABAC*1/2
            self.y = (Y) + ABAC*sqrt(3)/2

    def CHECK_BLUE(self,k,WIDE):
        X, Y = self.center
        self.x = max(X,self.x)
        self.y = max(-50*sqrt(3)*k+Y,min(50*sqrt(3)*k+Y,self.y))
        AC = self.x-100*k+X-25*WIDE, self.y-Y
        if self.y+sqrt(3)*self.x > Y+sqrt(3)*(100*k+X+25*WIDE):
            ABAC = (AC[0]-AC[1]*sqrt(3))/2
            self.x = (100*k+X+25*WIDE) + ABAC*1/2
            self.y = (Y) - ABAC*sqrt(3)/2
        if self.y-sqrt(3)*self.x < Y-sqrt(3)*(100*k+X+25*WIDE):
            ABAC = (AC[0]+AC[1]*sqrt(3))/2
            self.x = (100*k+X+25*WIDE) + ABAC*1/2
            self.y = (Y) + ABAC*sqrt(3)/2



class Ball(pygame.sprite.Sprite):
    def __init__(self):
        self.x, self.y = 0, 0
        self.r = ballRADIUS
        self.color = (220,50,220)
        self.vx, self.vy = 0, 0
        self.vz, self.z = 0, 0
        self.center = 0, 0
        self.hold = False
        self.thrown = None
        self.moves = []

    def draw(self, win):
        if self.hold: return
        self.color = (min(250,50+3*self.z),150,min(250,300-3*self.z))
        self.center = win.get_width()/2, win.get_height()/2
        X = self.x + self.center[0]
        Y = self.y + self.center[1]
        if self.thrown is None:
            pygame.draw.circle(win, WHITE, (X,Y), self.r+4)
        elif self.thrown.team == teamR:
            pygame.draw.circle(win, RED, (X,Y), self.r+4)
        elif self.thrown.team == teamB:
            pygame.draw.circle(win, BLUE, (X,Y), self.r+4)
        pygame.draw.circle(win, self.color, (X,Y), self.r)

    def move(self):
        self.vz -= GRAVITY*0.4
        if self.z == 0:
            self.vx = 0.7*self.vx
            self.vy = 0.7*self.vy
            self.vz = max(-0.7*self.vz, self.vz)
            self.thrown = None
        self.x += self.vx
        self.y += self.vy
        self.z = max(0,self.z+self.vz)
        self.CHECK(3.5,2)

    def CHECK(self,k,WIDE):
        X, Y = self.center
        if self.z < 0:
            self.z = 0
            self.vz = -self.vz*0.7
        if self.y > 50*sqrt(3)*k+Y or self.y < -50*sqrt(3)*k+Y:
            self.y = max(-50*sqrt(3)*k+Y,min(50*sqrt(3)*k+Y,self.y))
            self.vy = -self.vy
        AC = self.x+100*k-X+25*WIDE, self.y-Y
        if self.y+sqrt(3)*self.x < Y+sqrt(3)*(-100*k+X-25*WIDE):
            ABAC = (AC[0]-AC[1]*sqrt(3))/2
            self.x = (100*k+25*WIDE) - ABAC*1/2 + X
            self.y = ABAC*sqrt(3)/2 + Y
        if self.y-sqrt(3)*self.x > Y-sqrt(3)*(-100*k+X-25*WIDE):
            ABAC = (AC[0]+AC[1]*sqrt(3))/2
            self.x = (100*k+25*WIDE) - ABAC*1/2 + X
            self.y = -ABAC*sqrt(3)/2 + Y
        AC = self.x-100*k+X-25*WIDE, self.y-Y
        if self.y+sqrt(3)*self.x > Y+sqrt(3)*(100*k+X+25*WIDE):
            ABAC = (AC[0]-AC[1]*sqrt(3))/2
            self.x = -(100*k+25*WIDE) - ABAC*1/2 + X
            self.y = ABAC*sqrt(3)/2 + Y
        if self.y-sqrt(3)*self.x < Y-sqrt(3)*(100*k+X+25*WIDE):
            ABAC = (AC[0]+AC[1]*sqrt(3))/2
            self.x = -(100*k+25*WIDE) - ABAC*1/2 + X
            self.y = -ABAC*sqrt(3)/2 + Y


class BackGround(pygame.sprite.Sprite):
    def __init__(self, win):
        self.width = win.get_width()
        self.height = win.get_height()
        self.leftSide = pygame.Rect(0,0,self.width/2,self.height)
        self.rightSide = pygame.Rect(self.width/2,0,self.width/2,self.height)

    def draw(self, win):
        pygame.draw.rect(win, RED, self.leftSide)
        pygame.draw.rect(win, BLUE, self.rightSide)
        pygame.draw.polygon(win, WHITE, HEXAGON(4.1,self.width/2,self.height/2,2))
        pygame.draw.polygon(win, BLACK, HEXAGON(4.1,self.width/2,self.height/2,2), 15)
        pygame.draw.polygon(win, WHITE, HEXAGON(3.5,self.width/2, self.height/2,2))
        pygame.draw.polygon(win, BLACK, HEXAGON(3.5,self.width/2, self.height/2,2), 15)
        pygame.draw.line(win, BLACK, (self.width/2,0), (self.width/2,self.height), 10)


##############################################################