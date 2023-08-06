#!/usr/bin/env python

"""Simple module for getting amount of memory used by a specified user's
processes on a UNIX system.
It uses UNIX ps utility to get the memory usage for a specified username and
pipe it to awk for summing up per application memory usage and return the total.
Python's Popen() from subprocess module is used for spawning ps and awk.

"""

import subprocess
from os import environ

class MemoryMonitor(object):

    def __init__(self, username=environ['USER']):
        """Create new MemoryMonitor instance."""
        self.username = username
        memFile = file("/proc/meminfo", "r")
        self.totmem = int(memFile.readline()[9:].replace('kB',''))

    def usage(self):
        """Return int containing memory used by user's processes."""
        self.process = subprocess.Popen("ps -u %s -o rss | awk '{sum+=$1} END {print sum}'" % self.username,
                                        shell=True,
                                        stdout=subprocess.PIPE,
                                        )
        self.stdout_list = self.process.communicate()[0].split('\n')
        return int(self.stdout_list[0])

    def usagePerc(self):
        return (float(self.usage())/self.totmem)*100

def main():
    memory = MemoryMonitor()
    from time import sleep
    while True:
        from util import time2str
        print "%s memory = %.2f %%" %(time2str(), memory.usagePerc()) 
        sleep(1)

if __name__ == "__main__":
    main()
