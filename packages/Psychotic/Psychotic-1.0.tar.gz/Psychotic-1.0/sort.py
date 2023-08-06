import random
import sys

import psychotic

psychotic.full()

def sorter(n):
    data = [random.randint(0, n) for i in xrange(0, n)]
    data = sorted(data)

if __name__ == "__main__":
    sorter(int(sys.argv[1]))
    