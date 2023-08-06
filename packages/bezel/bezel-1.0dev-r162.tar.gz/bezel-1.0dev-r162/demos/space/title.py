from bezel.graphics.widgets import VBox
from bezel.graphics.widgets import Text, Button, Image

import math

from scene import SpaceScene
from game import GameScene

class DraggingImage(Image):
    def __init__(self, filename):
        super(DraggingImage, self).__init__(filename)
        self.last_angle = None
    
    def calc_angle(self, x, y):
        x = x - self.allocation[2] / 2.0
        y = y - self.allocation[3] / 2.0
        return math.atan2(y, x)
    
    def mouse_down(self, x, y, button):
        if button == 1:
            self.last_angle = self.calc_angle(x, y)
    
    def mouse_move(self, x, y, buttons):
        if buttons[0] and self.last_angle is not None:
            angle = self.calc_angle(x, y)
            delta = angle - self.last_angle
            self.rotation += delta * 180 / math.pi
            self.last_angle = angle

class TitleScene(SpaceScene):
    def __init__(self):
        super(TitleScene, self).__init__()
        
        sizer = VBox()
        
        self.title = Text('Generic Space Game', font_size=84,
                          alignment=Text.ALIGNMENT_CENTER)
        sizer.add(self.title)
        
        self.logo = DraggingImage('data/logo.png')
        sizer.add(self.logo)
        
        start = Button('Start Game', self.start_game)
        sizer.add(start)
        
        quit = Button('Quit', self.finish)
        sizer.add(quit)
        
        self.add(sizer)
        
        self.title_colour = (0, 0, 0)
    
    def start_game(self):
        game = GameScene()
        self.parent.add(game)
    
    def update(self, delay):
        super(TitleScene, self).update(delay)
        delta = delay / 10.0
        self.title_colour = [(x + i + delta) % 254
                             for i, x in enumerate(self.title_colour)]
        self.title.colour = [int(abs(x - 127) + 127) for x in self.title_colour]
        self.title.invalidate()
