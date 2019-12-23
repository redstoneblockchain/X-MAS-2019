mead = 0
flag = '0123456789'

def frobnicate(xor, offset, lvl):
  global mead
  mead = (xor + offset) / 2

  if (xor + 1 < offset):
    print(flag[mead])
    print("/")
    if (lvl == 3):
      mead = 8
    
    frobnicate(xor, mead, lvl+1)
    frobnicate(mead+1, offset, lvl+1)

frobnicate(0, len(flag), 0.0)
print(0)