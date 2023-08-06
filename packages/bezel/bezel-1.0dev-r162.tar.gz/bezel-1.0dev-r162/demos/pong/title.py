from bezel.graphics import Scene
from bezel.widgets.containers import VBox
from bezel.widgets import Text

from playing import PlayingGameState

class TitleScreen(Scene):
    def __init__(self):
        super(TitleScreen, self).__init__()
        
        white = (255, 255, 255)
        grey = (128, 128, 128)
        
        self.container = VBox()
        
        self.title = Text("PyPongy!", font_size=92, colour=white,
                          alignment=Text.ALIGNMENT_CENTER)
        self.container.add(self.title)
        
        self.subtitle = Text("A tutorial which got messed around with...",
                             font_size=16, colour=grey,
                             alignment=Text.ALIGNMENT_CENTER)
        self.container.add(self.subtitle)
        
        self.start = Text("Press any key to begin", font_size=16, colour=white,
                          alignment=Text.ALIGNMENT_CENTER)
        self.container.add(self.start)
        
        self.add(self.container)
    
    def key_down(self, key, unicode, mod):
        playing = PlayingGameState(unicode!='2')
        self.parent.add(playing)

