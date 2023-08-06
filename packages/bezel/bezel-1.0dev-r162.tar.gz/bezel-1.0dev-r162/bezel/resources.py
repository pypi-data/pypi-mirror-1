"""
This module borrows heavily from the pyglet.resources module,
which is licensed 
"""

import os
import pygame.image
import pygame.mixer

def get_ext(path):
    """Return the file extension from a path,
    without the extension seperater ('.')."""
    filename = os.path.split(path)[-1]
    ext = os.path.splitext(filename)[1]
    return ext.lstrip(os.path.extsep)

class Loader(object):
    file_loaders = {
        'png': pygame.image.load,
        'jpg': pygame.image.load,
        'bmp': pygame.image.load,
        'wav': pygame.mixer.Sound,
        'ogg': pygame.mixer.Sound,
        'mp3': pygame.mixer.Sound,
    }

    def __init__(self, path=None):
        self._index = {}
        self._cached_files = {}
        self.file_loaders = dict(self.file_loaders)
        if path is None:
            path = []
        self._path = path

        self.index_all()

    def index(self, path):
        """Recursively index all files in 'path'."""
        if not path in self._path:
            self._path.append(path)

        # Recursively index path.
        for root, dirs, files in os.walk(path):
            for name in files:
                filename = os.path.join(root, name)
                if get_ext(filename) in self.file_loaders:
                    location = os.path.abspath(filename)
                    if not filename in self._index:
                        self._index[filename] = location

    def index_all(self):
        """Recursively index all files in the current path."""
        self._index = {}
        for path in self._path:
            self.index(path)

    def load(self, filename):
        """Load filename using a file loader appropriate to it's extension."""
        if not filename in self._index:
            raise IOError('The file %s could not be found.' % filename)

        location = self._index[filename]

        if location in self._cached_files:
            return self._cached_files[location]
        else:
            ext = get_ext(location)
            loader = self.file_loaders[ext]

            data = self._cached_files[location] = loader(location)
            return data

    def load_all(self, callback=None):
        for path in self._path:
            for filename in self._index:
                data = self.load(filename)
                if callback is not None:
                    callback(filename, data)

_default_loader = Loader()

index = _default_loader.index
index_all = _default_loader.index_all
load = _default_loader.load
load_all = _default_loader.load_all

