class BaseTilemap(object):
    def __init__(self, map_size, tile_size, *args, **kwargs):
        super(BaseTilemap, self).__init__(*args, **kwargs)

        self.map_size = map_size
        self.tile_size = tile_size

        # An ordered list of layers containing Surfaces to blit.
        self.layers = []

    def add_layer(self, layer):
        self.layers.append(layer)

    def __iter__(self):
        # TODO: Add support for z values in data structures.
        z = 0
        for layer in self.layers:
            if isinstance(layer, dict):
                for x, y in layer:
                    item = layer[(x, y)]
                    yield (x, y, z), item
            else:
                for y, row in enumerate(layer):
                    for x, item in enumerate(row):
                        yield (x, y, z), item

