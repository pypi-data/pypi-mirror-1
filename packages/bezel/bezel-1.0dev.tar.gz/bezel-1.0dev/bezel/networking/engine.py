from SocketServer import StreamRequestHandler
import simplejson

def expose(fn):
    """
    Declares a function in the game engine to be part of the interface
    available through the networking engine.
    """
    fn.__exposed__ = True
    return fn

class DeclarativeMeta(type):
    def __new__(mcs, class_name, bases, new_attrs):
        cls = type.__new__(mcs, class_name, bases, new_attrs)
        cls.__classinit__.im_func(cls, new_attrs)
        return cls

class NetworkedGame(object):
    __metaclass__ = DeclarativeMeta
    __interface__ = None
    
    @classmethod
    def __classinit__(cls, new_attrs):
        interface = new_attrs.get('__interface__', {})
        for key, attr in new_attrs.items():
            if getattr(attr, '__exposed__', False):
                interface[key] = attr
        cls.__interface__ = interface
    
    def __call__(self, method, *args, **kwargs):
        return self.__interface__[method](self, *args, **kwargs)

def join(gen, num):
    items = []
    i = 0
    for item in gen:
        items.append(item)
        i += 1
        if i >= num:
            yield items
            items = []
            i = 0

class JSONRequestHandler(StreamRequestHandler, object):
    def __init__(self, *args, **kwargs):
        self.request_buffer = None
        self.engine = None
        super(JSONRequestHandler, self).__init__(*args, **kwargs)
    
    def get_data(self):
        while True:
            data = self.request.recv(1024)
            if not data:
                break
            yield data
    
    def get_lines(self):
        left_over = ''
        for data in self.get_data():
            data = left_over + data
            
            position = data.find('\n')
            while position != -1:
                yield data[:position+1].rstrip('\r\n')
                data = data[position+1:]
                position = data.find('\n')
            
            left_over = data
    
    def setup(self):
        super(JSONRequestHandler, self).setup()
        self.engine = self.server.engine

    def handle(self):
        super(JSONRequestHandler, self).handle()
        for method, args, kwargs in join(self.get_lines(), 3):
            args = simplejson.loads(args)
            kwargs = simplejson.loads(kwargs)
            
            assert isinstance(args, list)
            assert isinstance(kwargs, dict)
            
            kwargs = dict([(str(k), v) for k, v in kwargs.items()])
            
            response = self.engine(method, *args, **kwargs)
            response = simplejson.dumps(response)
            self.request.send(response + '\n')

