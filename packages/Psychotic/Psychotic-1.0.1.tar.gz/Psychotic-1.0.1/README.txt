Psychotic Python HyperOptimizer
-------------------------------

Release 1.0 (April 1, 2008)

HyperOptimizer for Python code, core CPython code and C extension modules.

Usage
-----

In your .py file:

  import psychotic
  psychotic.full()

Then, run your program normally. Psychotic will analyze the program and
produce an optimized .pyc compiled file. Here's an example:

  % python fact.py 10
  Psychotic Analysis Underway
  10! = 3628800

  Analysis complete. Initial run time: 0.00363612174988

As you can see, Psychotic will tell you when it's analyzing the program.
After doing the analysis, you can then run the optimized code:

  % python fact.pyc 10
  Psychotic Accelerated Executable
  10! = 3628800

  Accelerated run time: 0.0217978954315

Psychotic also tells you when you are running accelerated code.
Note that, as in this example, Psychotic may perform more slowly than running
Python alone for really small data sets, due to Psychotic's overhead.

License
-------

Copyright 2008 Kevin Dangoor. See LICENSE.txt for license terms.


History
-------

The Psyco project (http://psyco.sourceforge.net/) is an obvious predecessor to
Psychotic and is, indeed, the inspiration for the name.

The idea for Psychotic came up in discussions at PyCon 2008 in Chicago. A proof
of concept was created that night.

Additional inspiration comes from this thread on comp.lang.python:
http://groups.google.com/group/comp.lang.python/browse_frm/thread/df14a32d10432940/

The gist of that thread was that you can take a .pyc file and disassemble it
with Intel instructions (never mind that .pyc files are cross-platform).
The assumption is that if .pyc files are that powerful, we are not fully
taking advantage of them!

Constant Time Barrier
---------------------

In computer science, we learn about run time complexity:

http://en.wikipedia.org/wiki/Big_O_notation

The basic idea is that the size of the input data has an effect on
how long it takes the program to run. For example, we say that the
quicksort algorithm has a run time complexity of O(n log n), because
as the input size n grows, it takes n * log(n) time to run.

That means that people are penalized just because they have more data.
Does that seem fair?

In New Computer Science, we call this the "Constant Time Barrier".
Ideally, everything will run quickly regardless of how much data
you have.

Psychotic shatters the Constant Time Barrier.


The Psychotic Dingo
-------------------

The Psychotic Dingo is the bootstrap for your accelerated 
HyperOptimized Python programs. Like a wild, though not
rabid, dog, the Psychotic Dingo runs quite fast and your
program will too.

http://en.wikipedia.org/wiki/Dingo

http://flickr.com/photos/ogwen/59112447/

The analysis code lives in psychotic/alysis. The
Psychotic Dingo is in psychotic/dingo.py, of course.

Samples
-------

There are two sample programs included. These are the
same ones displayed in the screencast: fact.py (factorial
computation) and sort.py (sorting test).

Known Issues
------------

* does not work for GUI scripts
* does not work with Django, TurboGears, Pylons, Zope, Plone, Quixote, 
  CherryPy, Aquarium or really any web framework, actually.
* Different sets of command line options or other inputs may require
  reanalysis for optimum performance and correct behavior.
