class secureHash(object):
    def __init__(self):
        self.bits = 128
        self.mod = 2**128
        self.mask = 2**128 - 1
        self.step = 23643483844282862943960719738L
        self.hash = 9144491976215488621715609182563L

    def update(self, inp):
        for ch in inp:
            self.hash = ((self.hash + ord(ch)) * self.step) & self.mask

    def hexdigest(self):
        x = self.hash
        out = ''
        for i in range(self.bits/8):
            out=hex(x & 0xff)[2:].replace('L','').zfill(2)+out
            x >>= 8
        return out
