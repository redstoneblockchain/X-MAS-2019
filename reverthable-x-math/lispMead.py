
# The challenge-provided output.
target = [47, 22, 9, 55, -41, 59, 39, 97, -38, -38, 108, 42, 41, -47, -46, -38, -38, 22, 46, 110, 22, 46, 23, 20, 45, 46, 47, 20, -45, 46, 103]
print([chr((t ^ 42) + ord('0')) for t in target])

# Paste the TIO.run input here.
original =  '0123456789abcdefghijklmnopqrstuv'
# Paste the TIO.run output in here (must match target length).
scrambled = ''.join('g/8/4/2/1/3/6/5/7/c/a/9/b/e/d/f/o/k/i/h/j/m/l/n/s/q/p/r/u/t/v/0'.split('/'))

print(len(target))
print(len(original))
print(len(scrambled))

flag = ' ' * len(target)

def setflag(i, t):
  global flag
  flag = flag[:i] + chr((t ^ 42) + ord('0')) + flag[i+1:]

for i in range(0, len(original)):
  for j in range(0, len(target)):
    if original[i] == scrambled[j]:
      setflag(i, target[j])

print(flag)

