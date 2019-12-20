from hash import secureHash
import SocketServer
import string
import random
from text import *
import os
from hashlib import sha256

PORT = 2000
ROUNDS = 10
TIMEOUT = 120
sigma = string.ascii_letters+string.digits+'!@#$%^&*()-_=+[{]}<>.,?;:'

def isPrintable(x):
    global sigma

    alpha = set(sigma)
    beta = set(x)

    return alpha.intersection(beta) == beta    

def get_random_string(l, s):
    return ''.join([random.choice(s) for i in range(l)])

class ThreadedTCPRequestHandler(SocketServer.BaseRequestHandler):
    def PoW(self):
        s = os.urandom(10)
        h = sha256(s).hexdigest()
        self.request.sendall("Provide a hex string X such that sha256(X)[-6:] = {}\n".format(h[-6:]))
        inp = self.request.recv(2048).strip().lower()
        is_hex = 1
        for c in inp:
            if not c in '0123456789abcdef':
                is_hex = 0

        if is_hex and sha256(inp.decode('hex')).hexdigest()[-6:] == h[-6:]:
            self.request.sendall('Good, you can continue!\n')
            return True
        else:
            self.request.sendall('Oops, your string didn\'t respect the criterion.\n')
            return False

    def challenge(self, n):
        s = get_random_string(random.randint(30,35), sigma)
        H = secureHash()
        H.update(s)
        h = H.hexdigest()
        
        self.request.sendall(chall_intro.format(n, s, h))
        inp = self.request.recv(2048).strip()
        H_inp = secureHash()
        H_inp.update(inp)
        h_inp = H_inp.hexdigest()

        if(inp == s or not isPrintable(inp)):
            self.request.sendall(chall_wrong)
            return False    
        
        if(h_inp != h):
            self.request.sendall(chall_wrong)
            return False    

        self.request.sendall(chall_ok)
        return True

    def handle(self):
        self.request.settimeout(TIMEOUT)
        if not self.PoW():
            return
        self.request.sendall(intro.format(ROUNDS))

        for i in range(ROUNDS):
            if(not self.challenge(i+1)):
                self.request.sendall(losing_outro)
                return    

        self.request.sendall(winning_outro.format(FLAG))

        def finish(self):
            logger.info("%s client disconnected" % self.client_address[0])


class ThreadedTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    pass

if __name__ == '__main__':
    server = ThreadedTCPServer(('0.0.0.0', PORT), ThreadedTCPRequestHandler)
    server.allow_reuse_address = True
    server.serve_forever()

