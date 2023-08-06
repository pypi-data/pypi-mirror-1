import sys

import psychotic

psychotic.full()

def fact(n):
    val = n
    while n > 1:
        n -= 1
        val *= n
    return val

if __name__ == "__main__":
    print "%s! = %s" % (sys.argv[1], fact(int(sys.argv[1])))
    