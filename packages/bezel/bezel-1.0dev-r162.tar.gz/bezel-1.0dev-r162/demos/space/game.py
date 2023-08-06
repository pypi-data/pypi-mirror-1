from bezel.graphics.containers import Container
from bezel.graphics.widgets.image import Image

import math
import pygame

from scene import SpaceScene

class Ship(Image):
    def __init__(self, filename, has_inertia=True):
        super(Ship, self).__init__(filename)
        self.damping = 1
        
        self.has_inertia = has_inertia
        
        self.dx = 0
        self.dy = 0
    
    def rotate_backwards(self, amount):
        """
        Rotate so that the ship is facing the direction opposite to its
        direction of travel.
        """
        travelling = (math.atan2(self.dx, self.dy) * 180 / math.pi)
        travelling = travelling + 180
        facing = self.angle
        if abs(facing - travelling) < 1:
            self.angle = travelling
        elif (travelling - facing) % 360 > (facing - travelling) % 360:
            self.rotate(-amount)
        else:
            self.rotate(amount)
    
    def rotate(self, amount):
        self.rotation += amount
        
        if not self.has_inertia:
            angle = self.angle / 180 * math.pi
            speed = math.sqrt(self.dx**2 + self.dy**2)# * 0.95
            self.dx = math.sin(angle) * speed
            self.dy = math.cos(angle) * speed
    
    def accelerate(self, amount):
        angle = self.angle / 180.0 * math.pi
        dx, dy = math.sin(angle), math.cos(angle)
        
        self.dx += dx * amount
        self.dy += dy * amount
    
    def brake(self, amount):
        dx = math.sin(self.angle) * amount
        dy = math.cos(self.angle) * amount
        
        if self.dx * dx <= 0:
            dx = self.dx
        if self.dy * dy <= 0:
            dy = self.dy
        
        self.dx -= dx
        self.dy -= dy
    
    def update(self, delay):
        super(Ship, self).update(delay)
        x, y, w, h = self.allocation
        x += self.dx
        y += -self.dy
        
        x_bounds = (0, self.parent.allocation[2]-w)
        y_bounds = (0, self.parent.allocation[3]-h)
        if x < x_bounds[0] or x > x_bounds[1]:
            x = max([x_bounds[0], min([x, x_bounds[1]])])
            self.dx = (int(x < x_bounds[0]) * 2 - 1) * self.dx * self.damping
        if y < y_bounds[0] or y > y_bounds[1]:
            y = max([y_bounds[0], min([y, y_bounds[1]])])
            self.dy = (int(y < y_bounds[0]) * 2 - 1) * self.dy * self.damping
        
        self.invalidate()
        self.position = (x, y)
        self.invalidate()

class GameScene(SpaceScene):
    def __init__(self):
        super(GameScene, self).__init__()
        
        self.keys = set()
        
        self.container = Container()
        self.set_child(self.container)
        
        # Space ship
        self.ship = Ship('data/ship.png')
        self.container.add(self.ship)
        self.ship.rect = (0, 0, 64, 64)
    
    def key_down(self, key, unicode, mod):
        super(GameScene, self).key_down(key, unicode, mod)
        
        if key == pygame.K_i:
            self.ship.has_inertia = not self.ship.has_inertia
        
        if key in [pygame.K_UP, pygame.K_DOWN,
                   pygame.K_LEFT, pygame.K_RIGHT]:
            self.keys.add(key)
    
    def key_up(self, key, unicode, mod):
        super(GameScene, self).key_up(key, unicode, mod)
        if key in self.keys:
            self.keys.remove(key)
    
    def update(self, delay):
        super(GameScene, self).update(delay)
        if pygame.K_LEFT in self.keys:
            self.ship.rotate(-delay / 5.0)
        if pygame.K_RIGHT in self.keys:
            self.ship.rotate(delay / 5.0)
        if pygame.K_UP in self.keys:
            self.ship.accelerate(delay / 100.0)
        if pygame.K_DOWN in self.keys:
            if self.ship.has_inertia:
                self.ship.rotate_backwards(delay / 10.0)
            else:
                self.ship.brake(delay / 100.0)
