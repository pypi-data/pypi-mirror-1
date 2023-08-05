
import autoself

__metaclass__=autoself.autoself

class Test1:
    def __init__(color,size):
        self.color = color
        self.size = size
    def show():
        print "I am a " + self.size + ", " + self.color + " thing"

t = Test1("blue","big")

if not t.color == "blue":
    raise ValueError()
if not t.size == "big":
    raise ValueError()

