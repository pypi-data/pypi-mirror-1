from bezel.graphics.containers import Bin

class Scene(Bin):
    def __init__(self, *args, **kwargs):
        super(Scene, self).__init__(*args, **kwargs)

        self.stage = None

    def activate(self):
        pass

    def deactivate(self):
        pass

    def finish(self):
        self.stage.pop()

    def replace(self, next):
        self.stage.replace(next)

