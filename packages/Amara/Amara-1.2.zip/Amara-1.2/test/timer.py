#! /usr/bin/env python

"""Tool for measuring execution time of Python scripts

Based on timeit.py, modified by Jeremy Kloth for some code
simplification and to work with script bodies, rather than statements.


This module avoids a number of common traps for measuring execution
times.  See also Tim Peters' introduction to the Algorithms chapter in
the Python Cookbook, published by O'Reilly.

Command line usage:
    python timer.py [-n N] [-r N] [-p] [-v] [-h] file

Options:
  -r/--repeat N: how many times to repeat the timer (default 3)
  -p/--profile: profile execution
  -c/--calls: how many functions calls to display for profiling
  -v/--verbose: print raw timing results; repeat for more digits precision
  -h/--help: print this usage message and exit
  file: Python file to be timed (must define a main() function)

For plain timings, a suitable number of loops is calculated by trying
successive powers of 10 until the total time is at least 0.2 seconds.

The difference in default timer function is because on Windows,
clock() has microsecond granularity but time()'s granularity is 1/60th
of a second; on Unix, clock() has 1/100th of a second granularity and
time() is much more precise.  On either platform, the default timer
functions measure wall clock time, not the CPU time.  This means that
other processes running on the same computer may interfere with the
timing.  The best thing to do when accurate timing is necessary is to
repeat the timing a few times and use the best time.  The -r option is
good for this; the default of 3 repetitions is probably enough in most
cases.  On Unix, you can use clock() to measure CPU time.
"""

import gc
import sys
import time
import profile
import pstats

default_repeat = 3
default_calls = 50

if sys.platform == "win32":
    # On Windows, the best timer is time.clock()
    default_timer = time.clock
else:
    # On most other platforms the best timer is time.time()
    default_timer = time.time

def main(args=None):
    if args is None:
        args = sys.argv[1:]
    import getopt
    try:
        opts, args = getopt.getopt(args, "n:r:c:pvh",
                                   ["number=", "repeat=", "calls:",
                                    "profile", "verbose", "help"])
    except getopt.error, err:
        print err
        print "use -h/--help for command line help"
        return 2

    number = None
    repeat = default_repeat
    calls = default_calls
    verbose = 0
    precision = 3
    timeit = True
    help = False

    for o, a in opts:
        if o in ("-n", "--number"):
            number = int(a)
            if number <= 0:
                number = None # auto
        if o in ("-r", "--repeat"):
            repeat = int(a)
            if repeat <= 0:
                repeat = 1
        if o in ("-c", "--calls"):
            calls = int(a)
        if o in ("-p", "--profile"):
            timeit = False
        if o in ("-v", "--verbose"):
            if verbose:
                precision += 1
            verbose += 1
        if o in ("-h", "--help"):
            help = True

    if help or not args:
        print __doc__,
        return 0

    # Include the current directory, so that local imports work (sys.path
    # contains the directory of this script, rather than the current
    # directory)
    import os
    sys.path.insert(0, os.curdir)

    script = {}
    sys.argv = args
    script = {}
    execfile(args[0], script)
    try:
        script_main = script['main']
    except KeyError:
        print "unable to execute '%s': no main() function" % args[0]
        return 1

    if timeit:
        # determine number so that 0.2 <= total time < 2.0
        if number is None:
            for i in xrange(10):
                number = 10**i
                x = default_timer()
                for i in xrange(number):
                    script_main()
                x = default_timer() - x
                if verbose:
                    print "%d loops -> %.*g secs" % (number, precision, x)
                if x >= 0.2:
                    break

        timings = []
        seq = range(number)
        for i in xrange(repeat):
            gcold = gc.isenabled()
            gc.disable()
            start = default_timer()
            for i in seq:
                script_main()
            end = default_timer()
            timings.append(end - start)
            if gcold:
                gc.enable()
            gc.collect()
        best = min(timings)
        print "%d loops," % number,
        usec = best * 1e6 / number
    else:
        profiles = []
        for i in xrange(repeat):
            p = profile.Profile()
            p.runcall(script_main)
            stats = pstats.Stats(p)
            profiles.append((stats.total_tt, stats))
        best, stats = min(profiles)
        stats.strip_dirs()
        stats.sort_stats('cum').print_stats(calls)
        usec = best * 1e6

    if usec < 1000:
        print "best of %d: %.*g usec" % (repeat, precision, usec)
    else:
        msec = usec / 1000
        if msec < 1000:
            print "best of %d: %.*g msec" % (repeat, precision, msec)
        else:
            sec = msec / 1000
            print "best of %d: %.*g sec" % (repeat, precision, sec)
    return 0

if __name__ == "__main__":
    sys.exit(main())
