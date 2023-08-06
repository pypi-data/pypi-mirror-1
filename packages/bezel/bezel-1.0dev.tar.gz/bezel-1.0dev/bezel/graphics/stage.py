from bezel.graphics.containers import Bin

class Stage(Bin):
    def __init__(self):
        super(Stage, self).__init__()
        self.scene_stack = []

    # Children methods.
    def update_child(self):
        if self.child is not None:
            self.child.deactivate()
            self.child.stage = None

        child = self.scene_stack[-1]
        child.stage = self
        self.child = child
        self.child.activate()

        self.invalidate()

    def push(self, child):
        self.scene_stack.append(child)
        self.update_child()

    add = push

    def pop(self):
        assert len(self.scene_stack) > 0
        self.scene_stack.pop()
        self.update_child()

    def replace(self, child):
        self.scene_stack.pop()
        self.push(child)

