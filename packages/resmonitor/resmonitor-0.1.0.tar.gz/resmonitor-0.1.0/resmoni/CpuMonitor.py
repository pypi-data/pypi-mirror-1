 #!/usr/bin/env python

import os
import time

INTERVAL = 2
TIMEFORMAT = "%m/%d/%y %H:%M:%S"

def getTimeList():
    statFile = file("/proc/stat", "r")
    timeList = statFile.readline().split(" ")[2:6]
    statFile.close()
    for i in range(len(timeList))  :
        timeList[i] = int(timeList[i])
    return timeList

def deltaTime(interval=INTERVAL):
    x = getTimeList()
    time.sleep(interval)
    y = getTimeList()
    for i in range(len(x))  :
        y[i] -= x[i]
    return y

def getCpuPerc():
    dt = deltaTime()
    t = time.time()
    return 100 - (dt[len(dt) - 1] * 100.00 / sum(dt))

def main():
    from util import time2str
    
    while True  :    
        print "%s \t cpu = %.4f%%" %(time2str(), getCpuPerc())  


if __name__ == "__main__"  :
    main()
    
