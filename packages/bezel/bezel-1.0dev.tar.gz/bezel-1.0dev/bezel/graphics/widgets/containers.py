from bezel.graphics.containers import BaseContainer

class OrientedBox(BaseContainer):
    ORIENTATION_HORIZONTAL, ORIENTATION_VERTICAL = xrange(2)

    def __init__(self, orientation, *args, **kwargs):
        self.__orientation = orientation
        super(OrientedBox, self).__init__(*args, **kwargs)

    __orientation = None
    def get_orientation(self):
        return self.__orientation
    def set_orientation(self, orientation):
        previous = self.__orientation
        self.__orientation = orientation
        if previous != orientation:
            self.paint()
    orientation = property(get_orientation, set_orientation)

    def paint(self):
        super(OrientedBox, self).paint()
        sizes = [child.size for child in self.children]

        width, height = self.rect.size

        if self.orientation == OrientedBox.ORIENTATION_HORIZONTAL:
            req_height = max(sizes, key=lambda x: x[1])
            req_width = sum([size[0] for size in sizes])

            if req_width == 0:
                return

            hscale = width / req_width

            x = 0
            for child in self.children:
                child_width, child_height = child.size
                child_width *= hscale
                y = (height - child_height) / 2.0

                previous = tuple(child.rect.size)
                child.rect.topleft = int(x), int(y)
                child.rect.size = int(child_width), child_height

                if previous != child.rect.size:
                    child.paint()

                x += child_width

        elif self.orientation == OrientedBox.ORIENTATION_VERTICAL:
            req_width = max(sizes, key=lambda x: x[0])
            req_height = sum([size[1] for size in sizes])

            if req_height == 0:
                return

            vscale = height / req_height

            y = 0
            for child in self.children:
                child_width, child_height = child.size
                child_height *= vscale
                x = (width - child_width) / 2.0

                previous = tuple(child.rect.size)
                child.rect.topleft = int(x), int(y)
                child.rect.size = child_width, int(child_height)

                if previous != child.rect.size:
                    child.paint()

                y += child_height

class HBox(OrientedBox):
    def __init__(self, *args, **kwargs):
        super(HBox, self).__init__(HBox.ORIENTATION_HORIZONTAL,
                                   *args, **kwargs)

class VBox(OrientedBox):
    def __init__(self, *args, **kwargs):
        super(VBox, self).__init__(VBox.ORIENTATION_VERTICAL,
                                   *args, **kwargs)

