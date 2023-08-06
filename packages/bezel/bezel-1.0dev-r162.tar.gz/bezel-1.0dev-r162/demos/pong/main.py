#!/usr/bin/env python
from bezel.graphics import Display, Stage

from title import TitleScreen

class PongStage(Stage):
    def key_down(self, char, unicode, mod):
        super(PongStage, self).key_down(char, unicode, mod)
        if char == 27:
            self.parent.quit()

def main():
    # Create a new stage.
    stage = PongStage()
    
    # Add the title screen.
    title = TitleScreen()
    stage.add(title)
    
    # Create a display to show the stage.
    screen = Display(stage, 800, 600, 'PyPongy')
    screen.run()

if __name__ == '__main__':
    main()

