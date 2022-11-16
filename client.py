
import pygame
from network import Network
import pickle
from game import Game
from sprites import *

pygame.init()
WIDTH, HEIGHT = 1280, 720
win = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
font = pygame.font.SysFont("comicsans", 50)
background = BackGround(win)
pygame.display.set_caption("Client")

##############################################################
# Main Display (Integrate sprites in an event)               #
##############################################################

def updateDisplay(win, game):
    players, ball = game.players, game.ball
    background.draw(win)
    for p in players:
        if p.online: p.draw(win)
    ball.draw(win)
    if not game.ready:
        text = font.render("Waiting for Players...", 1, (255,0,0), True)
        textW, textH = text.get_width(), text.get_height()
        win.blit(text,(WIDTH/2-textW/2, HEIGHT/4-textH/2))
    elif game.counter >= 0:
        text = font.render(str(game.counter), 1, (255, 0, 0), True)
        if game.counter == 0:
            text = font.render("Dodge!", 1, (255, 0, 0), True)
        textW, textH = text.get_width(), text.get_height()
        win.blit(text,(WIDTH/2-textW/2, HEIGHT/4-textH/2))
    else:
        min, sec = (304-game.TIMER)//60, (304-game.TIMER)%60
        text = font.render(str(min)+" : "+str(sec), 1, (255,0,0), True)
        textW, textH = text.get_width(), text.get_height()
        win.blit(text,(WIDTH/10-textW/2, HEIGHT/10-textH/2))

    pygame.display.update()


##############################################################
# Main Pipeline                                              #
##############################################################

def main():
    run = True
    net = Network()                                            # create new network (connects user with server)
    ID = net.getID()
    print(ID)
    while run:
        clock.tick(60)
        keys = pygame.key.get_pressed()
        mousePos = pygame.mouse.get_pos()
        mousePos = (mousePos[0]-win.get_width()/2, mousePos[1]-win.get_height()/2)
        mouse = pygame.mouse.get_pressed(), mousePos
        game = net.send(keys,mouse)
        player = game.players[ID]
        player.myself = True
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
        updateDisplay(win, game)                                    # display two sprites

##############################################################

main()