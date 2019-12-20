bits = 128
mod = 2**bits
mask = 2**bits - 1
step = 23643483844282862943960719738
init = 9144491976215488621715609182563

class secureHash(object):
    def __init__(self):
        self.hash = init

    def update(self, inp):
        for ch in inp:
            self.hash = ((self.hash + ord(ch)) * step) & mask
        return self

    def hexdigest(self):
        x = self.hash
        out = ''
        for i in range(bits//8):
            out=hex(x & 0xff)[2:].replace('L','').zfill(2)+out
            x >>= 8
        return out
        
        
def getHashState(zeros):
  h = init
  for i in range(0, zeros):
    h = (h * step) & mask
  return h

def hashStr(s):
  return secureHash().update(s).hexdigest()

def hash(s):
  return secureHash().update(s).hash
 
 
 # h(abcd) = even * (h(abc) + d)
 #         = even * (even * (h(ab) + c) + d)
 
def matchOutput(targetI):
  print("Target int : 0x%x" % targetI)
  print("Target:  {0:b}".format(targetI))
  bytes = ''
  even = 'b'
  odd = 'c'
  for bit in range(1, bits+1):
    attempt = even + bytes
    h = hash(attempt)
    if False:
      print("Attempt %s hashes to %i = 0x%s" % (attempt, hash(attempt), hashStr(attempt)))
      print("Target:  " + "{0:b}".format(targetI)[-bit-2:])
      print("Current: " + "{0:b}".format(h)[-bit-2:])
    bit1 = bit + 1
    b = 1 << bit
    tb = (targetI & b) >> bit
    hb = (h & b) >> bit
    #print(tb)
    #print(hb)
    if tb == hb:
      bytes = odd + bytes
    else:
      bytes = even + bytes
      #if tb > 0:
      #else:
       # bytes = even + bytes
      
    h = hash(bytes)
    if False:
      print("Choice %s hashes to %i = 0x%s" % (bytes, hash(bytes), hashStr(bytes)))
      print("Target:  " + "{0:b}".format(targetI)[-bit-2:])
      print("Current: " + "{0:b}".format(h)[-bit-2:])
      print((targetI & b) >> bit)
      print((h & b) >> bit)
      print("--------------------------------")
    #print("({0:b} + {1:b}) * {2:b} & {3b} = {4:b}".format(h, bytes[0], step, mask, ((h + bytes[0]) step)))
  return bytes

if False:
  print("{0:b}".format(hash('bbbbbbbbbbbbbbbbbbbbbbbbbb')))
  print("%x" % hash('bbbbbbbbbbbbbbbbbbbbbbbbbb'))
  print((((hash('ab') + ord('c')) * step + ord('d')) * step) & mask)
  print(((hash('abc') + ord('d')) * step) & mask)
  print(hash('abcd') & mask)
  exit(0)

obj1 = ']5ZOQljM01T[3,k=8Soef*[3vlD2L1w!'
#obj2 = '\x00' * bits + obj1
#obj3 = obj1 + '\x00' * bits
#obj4 = obj1 + 'lkashgflakhs' + '\x00' * bits

s1 = secureHash().update(obj1).hexdigest()
#s2 = secureHash().update(obj2).hexdigest()
#s3 = secureHash().update(obj3).hexdigest()
#s4 = secureHash().update(obj4).hexdigest()

print("%s hashes to %i = 0x%s" % (obj1, hash(obj1), hashStr(obj1)))
#print(s2)
#print(s3)
#print(s4)

coll = matchOutput(hash(obj1))
print("%s hashes to %i = 0x%s" % (coll, hash(coll), hashStr(coll)))

exit(0)
    
h = 1
i = 0
for c in range(0, 255):
  print("%x" % ((c * step) & mask))
  
print('---')

h = 1
for i in range(0, bits + 2):
  h = (h * step) & mask
  print("%32x, %s" % (h, hash('\x00' * i)))

  
  
  
