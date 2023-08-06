import socket
import simplejson

class GameEngineProxy(object):
    """
    A class which provides the same attributes of the server's game
    engine, on the fly.
    """
    def __init__(self, client):
        self.__client = client
    
    def __getattribute__(self, name):
        try:
            return super(GameEngineProxy, self).__getattribute__(name)
        except AttributeError:
            def fn(*args, **kwargs):
                return self.__client.request(name, *args, **kwargs)
            setattr(self, name, fn)
            return fn

class JSONGameClient(object):
    def __init__(self, host, port):
        self.server_address = (host, port)
        self.socket = socket.socket()
        self.socket.connect(self.server_address)
        
        self.engine = GameEngineProxy(self)
        
        self.buffer = ''
    
    def __del__(self):
        self.socket.close()
    
    def send(self, data):
        self.socket.send(data + '\n')
    
    def read(self):
        position = self.buffer.find('\n')
        while position == -1:
            self.buffer += self.socket.recv(1024)
            position = self.buffer.find('\n')
        
        result = self.buffer[:position+1].rstrip('\r\n')
        self.buffer = self.buffer[position+1:]
        return result
    
    def request(self, message, *args, **kwargs):
        args = simplejson.dumps(args)
        kwargs = simplejson.dumps(kwargs)
        data = '\n'.join([message, args, kwargs])
        self.send(data)
        response = self.read()
        return simplejson.loads(response)

