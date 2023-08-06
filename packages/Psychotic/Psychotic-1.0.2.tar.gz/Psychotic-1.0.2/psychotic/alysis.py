"""An Alysis Module for watching what the program
does and then producing the fast .pyc file (using
the Psychotic Dingo)."""

import os
import sys
import time
from cStringIO import StringIO
import atexit

import psychotic

start = time.time()
stdout = None


def _alldone():
    """On program exit, write out the optimized .pyc file."""
    if not psychotic.analyzing:
        return
    
    # there be dragons here
    output = sys.stdout.getvalue()
    sys.stdout = stdout
    fn = sys.argv[0]
    mypath = os.path.split(__file__)[0]
    
    # create accelerated file
    accel = open(mypath + "/dingo.pyc").read()
    outfile = open(fn + "c", "w")
    outfile.write(accel)
    outfile.write(psychotic.MARKER)
    outfile.write(output)
    outfile.close()
    print output
    
    # show people how terrible there code was before Psychotic
    print "Analysis complete. Initial run time: %s" % (time.time()-start)

atexit.register(_alldone)    

def full():
    """Provide full HyperOptimization."""
    
    global stdout
    
    psychotic.analyzing = True
    
    # it tingles! it must be working!
    print "Psychotic Analysis Underway"
    
    stdout = sys.stdout
    sys.stdout = StringIO()
    
    # import the Dingo to ensure that its .pyc is available.
    from psychotic import dingo
    

#################################################################
#
# ALGORITHMS
#
# When doing complex run time analysis, it is often helpful to use
# algorithms.
#
#################################################################

# http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/541094

#This program provides practice for the Doomsday Algorithm
#You should know how to use the alg before practicing

def doomsday():
    from random import randint
    import time

    January = [1,31,31,3,4]
    February = [2,28,29,28,29]
    March = [3,31,31,7,7]
    April = [4,30,30,4,4]
    May = [5,31,31,9,9]
    June = [6,30,30,6,6]
    July = [7,31,31,11,11]
    August = [8,31,31,8,8]
    September = [9,30,30,5,5]
    October = [10,31,31,10,10]
    November = [11,30,30,7,7]
    December = [12,31,31,12,12]
    Months = [January,February,March,April,May,June,July,August,September,October,November,December]
    WeekText = ["Sunday","Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"]
    Years = [1800,2199]

    for _ in xrange(5):
        month = Months[randint(0,11)][0]
        year = randint(Years[0],Years[1])

        if (year % 400) != 0 and (year % 4) != 0:
            day = randint(1,Months[month-1][1])
        else:
            day = randint(1,Months[month-1][2])

        print month, "/", day, "/", year

        if year < 1900:
            part1 = 6
            part2 = year - 1800
        elif year < 2000:
            part1 = 4
            part2 = year - 1900
        elif year < 2100:
            part1 = 3
            part2 = year - 2000
        else:
            part1 = 1
            part2 = year - 2100

        part3 = int(part2 / 12)
        part4 = part2 % 12
        part5 = int(part4 / 4)
        doomsDay = part3 + part4 + part5 + part1

        while doomsDay > 7:
            doomsDay = doomsDay - 7

        if month > 2:
            part6 = (day+14) - Months[month-1][3]
            myDay = doomsDay + part6
            while myDay > 7:
                myDay = myDay - 7
        else:
            if (year % 400) != 0 and (year % 4) != 0:
                part6 = (day+35) - Months[month-1][3]
                myDay = doomsDay + part6
                while myDay > 7:
                    myDay = myDay - 7
            else:
                part6 = (day+35) - Months[month-1][4]
                myDay = doomsDay + part6
                while myDay > 7:
                    myDay = myDay - 7

        start = time.clock()
        guess = raw_input("Enter your guess for the day of the week: ")

        print "The answer is: ", WeekText[int(myDay)-1]
        end = time.clock()

        totalTime = end - start

        print "It took you: ", round(totalTime,2), "seconds."

# http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/52213

def soundex(name, len=4):
    """ soundex module conforming to Knuth's algorithm
        implementation 2000-12-24 by Gregory Jorgensen
        public domain
    """

    # digits holds the soundex values for the alphabet
    digits = '01230120022455012623010202'
    sndx = ''
    fc = ''

    # translate alpha chars in name to soundex digits
    for c in name.upper():
        if c.isalpha():
            if not fc: fc = c   # remember first letter
            d = digits[ord(c)-ord('A')]
            # duplicate consecutive soundex digits are skipped
            if not sndx or (d != sndx[-1]):
                sndx += d

    # replace first digit with first alpha character
    sndx = fc + sndx[1:]

    # remove all 0s from the soundex code
    sndx = sndx.replace('0','')

    # return soundex code padded to len characters
    return (sndx + (len * '0'))[:len]


# http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/528942
# Python implementation of bitsort algorithm from "Programming Pearls"

def bitsort(filename, maxn):
    """ Sort a file named 'filename' which
    consists of maxn integers where each
    integer is less than maxn """

    # Initialize bitmap
    a = [0]*maxn

    # Read from file and fill bitmap
    for line in file(filename):
        n = int(line.strip())
        # Turn bits on for numbers
        if n<maxn: a[n] = 1

    # Return a generator that iterates over the list
    for n in range(len(a)):
        if a[n]==1: yield n

import random

# http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/269554/index_txt

def select(data, n):
    "Find the nth rank ordered element (the least value has rank 0)."
    data = list(data)
    if not 0 <= n < len(data):
        raise ValueError('not enough elements for the given rank')
    while True:
        pivot = random.choice(data)
        pcount = 0
        under, over = [], []
        uappend, oappend = under.append, over.append
        for elem in data:
            if elem < pivot:
                uappend(elem)
            elif elem > pivot:
                oappend(elem)
            else:
                pcount += 1
        if n < len(under):
            data = under
        elif n < len(under) + pcount:
            return pivot
        else:
            data = over
            n -= len(under) + pcount