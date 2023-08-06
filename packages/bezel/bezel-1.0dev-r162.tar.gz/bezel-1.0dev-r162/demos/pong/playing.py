from bezel.graphics import Scene, Widget

from bezel.widgets import Container, Text

import random
import math

import pygame
from pygame.constants import *
from done import GameOver

PADDLE_SPEED = 20

class PlayingGameState(Scene):
    def __init__(self, use_ai):
        super(PlayingGameState, self).__init__()
        
        self.container = Container()
        self.add(self.container)
        
        self.ball = Ball()
        w, h = self.ball.size_request()
        self.ball.allocation = (0, 0, w, h)
        self.container.add(self.ball)
        
        if use_ai:
            self.player1 = Paddle((15, 75), 480)
            self.player2 = AIPaddle((15, 75), 480, self.ball)
        else:
            self.player1 = Paddle((15, 75), 480, upkey=K_w, downkey=K_s)
            self.player2 = Paddle((15, 75), 480)
        
        w, h = self.player1.size_request()
        self.player1.allocation = (0, 0, w, h)
        self.container.add(self.player1)
        
        w, h = self.player2.size_request()
        self.player2.allocation = (0, 0, w, h)
        self.container.add(self.player2)
        
        self.score1 = Score()
        w, h = self.score1.size_request()
        self.score1.allocation = (0, 0, 0, 0)
        
        self.score2 = Score()
        w, h = self.score2.size_request()
        self.score2.allocation = (0, 0, 0, 0)
    
    def size_allocate(self, x, y, width, height):
        super(PlayingGameState, self).size_allocate(x, y, width, height)
        self.ball.center()
        self.player2.allocation = (width - 15,) + self.player2.allocation[1:4]
    
    def update(self,delay):
        self.player1.collidesWithBall(self.ball)
        self.player2.collidesWithBall(self.ball)
        
        super(PlayingGameState, self).update(delay)
        
        score = 0
        if (self.ball.outOfBounds < 0):
            score = self.score2.getScore() + 1
            self.score2.setScore(score)
        elif (self.ball.outOfBounds > 0):
            score = self.score1.getScore() + 1
            self.score1.setScore(score)
        
        if score:
            self.ball.center()
            if(score >= 3):
                done = GameOver(self.score1, self.score2)
                self.replace(done)

class Score(Text):
    def __init__(self, initial_score=0):
        super(Score, self).__init__(str(initial_score), font_size=36, colour=(255, 255, 255))
        self.setScore(initial_score)
    
    def setScore(self, score):
        self.score = score
        self.text = str(score)
    
    def getScore(self):
        return self.score

class Ball(Widget):
    
    AXIS_X = 1
    AXIS_Y = 2
    
    def __init__(self, radius=16, speed=110, increase=0.1):
        """The 'bounds' parameter indicates the width and height
        of the playing area"""
        super(Ball, self).__init__((radius*2, radius*2))
        self.radius = radius
        self.speed = speed
        self.increase = increase
        self.originalSpeed = speed
        self.dx = self.dy = 0
    
    def bounce(self, axis):
        if(axis & self.AXIS_X):
            self.dx = -self.dx
        if(axis & self.AXIS_Y):
            self.dy = -self.dy
        
        self.speed += self.speed * self.increase
    
    def center(self):
        loc = [self.parent.allocation[2] / 2,
               self.parent.allocation[3] / 2]
        
        if random.randint(0, 1):
            angle = random.randint(45, 135)
        else:
            angle = random.randint(225, 315)
        
        angle = math.radians(angle)
        self.dx = math.sin(angle)
        self.dy = math.cos(angle)
        self.outOfBounds = 0
        self.speed = self.originalSpeed
        
        rect = list(self.allocation)
        rect[0:2] = loc
        self.allocation = tuple(rect)
    
    def paint(self, screen, clip):
        pygame.draw.circle(screen, (255,255,0), (self.allocation[2]/2, self.allocation[3]/2), self.radius)
    
    def update(self, delay):
        x,y = self.allocation[0:2]
        radius = self.radius
        toMove = delay * self.speed / 1000
        moveX = self.dx * toMove
        moveY = self.dy * toMove
        
        newX = x + moveX
        newY = y + moveY
        
        if (newY < 0 or newY > self.parent.allocation[3] - radius):
            self.bounce(self.AXIS_Y)
            moveY = self.dy * toMove * 2
            newY = y + moveY
        if (newX < 0):
            self.outOfBounds = -1
        elif (newX > self.parent.allocation[2]):
            self.outOfBounds = 1
        
        self.invalidate()
        rect = list(self.allocation)
        rect[0:2] = int(newX), int(newY)
        self.allocation = tuple(rect)
        self.invalidate()

class Paddle(Widget):
    def __init__(self, size, maxY, upkey=K_UP, downkey=K_DOWN):
        super(Paddle, self).__init__(size)
        self.maxY = maxY
        self.dy = 0
        self.speed = PADDLE_SPEED
        self.upkey = upkey
        self.downkey = downkey
    
    def collidesWithBall(self, ball):
        paddle_rect = pygame.Rect(*self.allocation)
        ball_rect = pygame.Rect(*ball.allocation)
        
        if paddle_rect.colliderect(ball_rect):
            ball.bounce(Ball.AXIS_X)
            return True
        return False
    
    def update(self,delay):
        x, y = self.allocation[0:2]
        
        delay /= 100.0
        
        moveY = delay * self.speed * self.dy
        
        newY = y + moveY
        
        top = 10
        bottom = self.parent.allocation[3] - top
        if newY < top:
            newY = top
        elif newY > bottom:
            newY = bottom
        
        self.invalidate()
        
        rect = list(self.allocation)
        rect[1] = newY
        self.allocation = tuple(rect)
        
        self.invalidate()
    
    def key_down(self, key, unicode, mod):
        if key == self.upkey:
            self.dy = -1
        elif key == self.downkey:
            self.dy = 1
    
    def key_up(self, key, unicode, mod):
        if key == self.upkey and self.dy == -1:
            self.dy = 0
        elif key == self.downkey and self.dy == 1:
            self.dy = 0
    
    def paint(self, surface, clip):
        pygame.draw.rect(surface, (255, 255, 255), clip)

class AIPaddle(Paddle):
    def __init__(self, size, maxY, ball):
        super(AIPaddle, self).__init__(size, maxY)
        self.ball = ball
    
    def key_down(self, key, unicode, mod):
        pass
    
    def key_up(self, key, unicode, mod):
        pass
    
    def update(self, delay):
        super(AIPaddle, self).update(delay)
        
        py = self.allocation[1] + self.allocation[3]
        by = self.ball.allocation[1] + (self.ball.allocation[3] / 2.0)
        
        buf = self.ball.speed * self.ball.dy
        
        if py - buf < by:
            self.dy = 1
        elif py - buf > by + self.allocation[3]:
            self.dy = -1
        else:
            self.dy = 0

