from bezel.networking.engine import NetworkedGame, expose

class GameEngine(NetworkedGame):
    def __init__(self, *args, **kwargs):
        super(GameEngine, self).__init__(*args, **kwargs)
        self.count = 0
    
    @expose
    def say(self, something):
        return 'Simon says "%s"' % something
    
    @expose
    def add(self, num):
        self.count += num
        return self.count

