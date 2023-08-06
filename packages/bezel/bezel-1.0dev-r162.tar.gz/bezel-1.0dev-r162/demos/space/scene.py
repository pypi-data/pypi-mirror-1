from bezel.graphics.scene import Scene

class SpaceScene(Scene):
    def key_down(self, char, unicode, mod):
        super(SpaceScene, self).key_down(char, unicode, mod)
        if char == 27:
            self.finish()
