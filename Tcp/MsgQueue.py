class MsgQueue():
    def __init__(self, limiter = "|"):
        self.queue = b""
        self.ready = []
        self.limiter = limiter

    def push(self, msg:bytes):
        if not isinstance(msg, bytes):
            raise "Bytes required" 
        
        self.queue += msg

        msgs = self.queue.split(self.limiter)
        n = len(msgs) if msgs[-1] == b"" else len(msgs) - 1

        for i in range(n):
            self.ready.append(msgs[i])

        self.queue = msgs[-1]

    def pop(self):
        if len(self.ready) == 0:
            return b""

        return self.ready.pop(0)