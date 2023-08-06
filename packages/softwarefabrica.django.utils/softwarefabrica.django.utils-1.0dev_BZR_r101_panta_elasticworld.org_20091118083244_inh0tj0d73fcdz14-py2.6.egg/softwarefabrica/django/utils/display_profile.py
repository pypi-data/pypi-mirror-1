#!/usr/bin/env python

# display profile/cProfile/hotshot profile results

import sys
from pstats import Stats

def main():
    # load the test file generated above
    stats = Stats(sys.argv[1]) 
    # order by time and cumulative time for only py files
    stats.sort_stats('time', 'cumulative').print_stats('.py')

if __name__ == '__main__':
    main()
