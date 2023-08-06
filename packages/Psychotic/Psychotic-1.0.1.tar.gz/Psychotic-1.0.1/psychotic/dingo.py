"""The Psychotic Dingo

The Psychotic Dingo is the bootstrap for your accelerated 
HyperOptimized Python programs. Like a wild, though not
rabid, dog, the Psychotic Dingo runs quite fast and your
program will too.

http://en.wikipedia.org/wiki/Dingo

http://flickr.com/photos/ogwen/59112447/
"""

import psychotic

# during analysis, do not load the bootstrap.
if not psychotic.analyzing:
    # let everyone know what a great job we're doing.
    print "Psychotic Accelerated Executable"
    
    import time
    start = time.time()
    import random
    
    # see how fast this program can run?
    # TODO in a future version, we can
    # make this twice as fast.
    time.sleep(float(random.randint(1,50))/1000)
    
    # Execute the code
    # TODO there seem to be some minor 
    # problems when we change the input
    # data. Revisit in 2.0.
    me = open(__file__).read()
    location = me.index(psychotic.MARKER)
    print me[location+len(psychotic.MARKER):]
    
    # really, we are doing a great job. See?
    print "Accelerated run time: %s" % (time.time()-start)
