import os, sys
from secret import flag

items = []

def menu():
    print "SANTA's Decoration shop yay!"
    print "1. Add new decoration to the shopping list"
    print "2. View your shopping list"
    print "3. Ask Santa for a suggestion"

    sys.stdout.write ("Your choice: ")
    sys.stdout.flush ()
    return sys.stdin.readline ()

class Decoration(object):
    def __init__(self, type, quantity):
        self.quantity = quantity
        self.type = type
    def print_decoration(self):
        print ('{0.quantity} x ... '+ self.type).format(self)

def leak_source_code():
    print "Santa shows you how his shop works to prove that he doesn't scam you!\n\n"

    with open(__file__, 'r') as f:
        print f.read()

def add_item():
    sys.stdout.write ("What item do you like to buy? ")
    sys.stdout.flush ()
    type = sys.stdin.readline ().strip ()

    sys.stdout.write ("How many of those? ")
    sys.stdout.flush ()
    quantity = sys.stdin.readline ().strip () # Too lazy to sanitize this

    items.append(Decoration(type, quantity))

    print 'Thank you, your items will be added'

def show_items():
    for dec in items:
        dec.print_decoration()

print ("""       ___
     /`   `'.
    /   _..---;
    |  /__..._/  .--.-.
    |.'  e e | ___\\_|/____
       (_)'--.o.--|    | |    |
      .-( `-' = `-|____| |____|
     /  (     |____   ____|
     |   (    |_   | |  __|
     |    '-.--';/'/__ | | (  `|
     |      '.   \\    )"";--`\\ /
     \\    ;   |--'    `;.-'
     |`-.__ ..-'--'`;..--'`
     """)

while True:
    choice = menu().strip ()

    if(choice == '1'):
        add_item()
    elif(choice == '2'):
        show_items()
    elif(choice == '3'):
        leak_source_code()
    else:
        print "Invalid choice"
