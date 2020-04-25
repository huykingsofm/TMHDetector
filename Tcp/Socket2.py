import socket
from .MsgQueue import MsgQueue

class Socket2():
    limiter = b"|"
    def __init__(self, **kwargs):
        if "socket" in kwargs.keys():   
            self.__socket__ = kwargs["socket"]
        
        if "family" in kwargs.keys() and "type" in kwargs.keys():
            self.__socket__ = socket.socket(kwargs["family"], kwargs["type"])

    def sendall(self, data):
        data += Socket2.limiter
        return self.__socket__.sendall(data)
    
    def send(self, data):
        data += Socket2.limiter
        return self.__socket__.sendall(data)

    def recv(self, buffer = 1024):
        return self.__socket__.recv(buffer)

    def bind(self, addr):
        return self.__socket__.bind(addr)

    def connect(self, addr):
        return self.__socket__.connect(addr)

    def listen(self, backlog):
        return self.__socket__.listen(backlog)

    def accept(self):
        conn, addr = self.__socket__.accept()
        conn = Socket2(socket = conn)
        return conn, addr

    def close(self):
        return self.__socket__.close()

    def settimeout(self, timeout):
        return self.__socket__.settimeout(timeout)

    def getsockname(self):
        return self.__socket__.getsockname()