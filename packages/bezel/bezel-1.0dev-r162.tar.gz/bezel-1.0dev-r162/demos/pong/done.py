from bezel.graphics import Scene
from bezel.widgets import Container

import pygame
from pygame.constants import *

class GameOver(Scene):
    def __init__(self, score1, score2):
        super(GameOver, self).__init__()
        
        self.container = Container()
        
        self.timer = 0
        
        if score1.getScore() > score2.getScore():
            winner = 1
        else:
            winner = 2
        
        self.messageFont = pygame.font.Font(None,36)
        self.font = pygame.font.Font(None, 20)
        
        self.setMessage("Player %d wins!" % winner)
        
        self.score1 = score1
        self.container.add(self.score1)
        self.score2 = score2
        self.container.add(self.score2)
        
        self.add(self.container)
    
    def setMessage(self, message):
        self.message = message
        self.msgImage = self.messageFont.render(message, 0, (255,255,255))
    
    def paint(self, screen, clip):
        super(GameOver, self).paint(screen, clip)
        w = screen.get_width()
        h = screen.get_height()
        
        surface = self.msgImage
        centerX = w/2 - surface.get_width()/2
        centerY = h*0.25 - surface.get_height()/2
        screen.blit(surface, (centerX,centerY))
        
        surface = self.messageFont.render("to",0,(255,255,255))
        centerX = w/2 - surface.get_width()/2
        centerY = h/2 - surface.get_height()/2
        screen.blit(surface, (centerX,centerY))
        
        rect = list(self.score1.allocation)
        rect[0:2] = (w/2-rect[2], int(h*0.375))
        self.score1.allocation = tuple(rect)
        
        rect = list(self.score2.allocation)
        rect[0:2] = (w/2-rect[2], int(h*0.625))
        self.score2.allocation = tuple(rect)
    
    def update(self, delay):
        self.timer += delay
        if self.timer > 2000:
            self.finish()

