import socket
from .MsgQueue import MsgQueue
import threading
import time
from .Socket2 import Socket2

class TcpServer():
    limiter = b"|"

    def __init__(self, ip, port, solver, buffer = 1024):
        self.__MQ__ = []
        self.socket = Socket2(family = socket.AF_INET, type = socket.SOCK_STREAM)
        self.__stop__ = False
        self.__buffer__ = buffer
        self.__solver__ = solver
        self.socket.bind((ip, port))

    def start_listen(self, deamon = False):
        t = threading.Thread(target = self.__start_listen__)
        t.setDaemon(deamon)
        t.start()
        print("Server started service...Done")

    def __start_listen__(self):
        self.socket.listen(1)
        while not self.__stop__:
            conn, addr = self.socket.accept()
            self.__MQ__.append(MsgQueue(limiter= TcpServer.limiter))
            
            t = threading.Thread(target=self.__serve__, args= (conn, addr, self.__MQ__[-1]))
            t.start()

            t = threading.Thread(target=self.__solve__, args= (conn, addr, self.__MQ__[-1]))
            t.start()
            print("Start connection with {}".format(addr))
        self.socket.close()

    def stop_listen(self):
        self.__stop__ = True

    def __serve__(self, conn: socket, addr, MQ):
        while True:
            try:
                data = conn.recv(self.__buffer__)
            except Exception as e:
                print(str(e))
                break

            if not data:
                break

            MQ.push(data)

        MQ.push(b"exit|")

    def __solve__(self, conn, addr, MQ: MsgQueue):
        while True:
            data = MQ.pop()
            if not data:
                time.sleep(0.1)
                continue
            if data == b"exit":
                break

            self.__solver__(conn, addr, data, server = self)
        print("Stop connection with {}".format(addr))

class TcpClient():
    limiter = b"|"

    def __init__(self, solver, buffer = 1024, verbose = True, error_log = True):
        self.__MQ__ = MsgQueue(TcpClient.limiter)
        self.socket = Socket2(family = socket.AF_INET, type = socket.SOCK_STREAM)
        self.__buffer__ = buffer
        self.__solver__ = solver
        self.__verbose__ = verbose
        self.__err_log__ = error_log

    def __print__(self, data):
        if self.__verbose__:
            print(data)

    def __log__(self, error):
        if self.__err_log__:
            print(error)

    def connect(self, ip, port, timeout = 0.5):
        self.__print__("Connecting with server {}:{}".format(ip, port))
        try:
            conn = self.socket.connect((ip, port))
            self.__print__("Connecting with server {}:{} successfully".format(ip, port))
        except Exception as e:
            self.__log__(str(e))
            return None

        self.__addr__ = "({}:{})".format(ip, port)
        return conn
    def __serve__(self):
        while True:
            try:
                data = self.socket.recv(self.__buffer__)
            except socket.error as e:
                self.__log__(str(e))
                break

            if not data:
                break

            self.__MQ__.push(data)

        self.__MQ__.push(b"exit|")

    def __solve__(self):
        while True:
            data = self.__MQ__.pop()
            if not data:
                time.sleep(0.1)
                continue
            if data == b"exit":
                break

            self.__solver__(self.socket, self.__addr__, data, client = self)
        self.__print__("Stop connection to server {}".format(self.__addr__))

    def start(self, deamon = False):
        self.__print__("Client start at {}".format(self.socket.getsockname()))
        self.__t1__ = threading.Thread(target = self.__serve__)
        self.__t1__.setDaemon(deamon)
        self.__t1__.start()

        self.__t2__ = threading.Thread(target = self.__solve__)
        self.__t2__.setDaemon(deamon)
        self.__t2__.start()

    def isconnect(self):
        if self.__t1__.isAlive() or self.__t2__.isAlive():
            return True
        return False

    def close(self):
        self.socket.close()