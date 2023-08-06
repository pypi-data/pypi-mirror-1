 #!/usr/bin/env python
''' UsageDB store cpu and memory usage '''
import os
try:
    import sqlite3 as sqlite
except: 
    import sqlite


dbname = 'usage.db'

from util import *
from time import time
from datetime import datetime, timedelta

def getEpochCpuMemFrom(data):
    try:
        from numpy import array
        a = array(data)
        return a[:,0], a[:,1], a[:,2]

    except:
        epochs = []
        cpus = []
        mems = []
        for epoch, cpu, mem in data:
            epochs.append(epoch)
            cpus.append(cpu)
            mems.append(mem)
        return epochs, cpus, mems

def genPng(data, fname='graph.png', rotation=20, nxlabel=10):
    epochs, cpus, mems = getEpochCpuMemFrom(data)

    nxlabel = min(len(epochs), nxlabel)
    # take only nxlabel position xlabel
    xpos = range(0, len(epochs),  max(1,len(epochs)/10))
    xepochs = [epochs[i] for i in xpos]
    xlabels = [datetime2str(epoch2datetime(e),'%H:%M (%d)') for e in xepochs]
    
    ypos = range(0, 101, 25)
    perclabels = [str(x) for x in ypos]
    
    
    import pylab
    pylab.grid(True)
    pylab.subplot(8,1,1)
    pylab.grid(True)
    pylab.plot(epochs, cpus,'-g')
    pylab.xlabel("time")
    pylab.ylabel("CPU %")
    pylab.title("CPU usage")
    pylab.xticks(xepochs, xlabels, rotation=rotation, fontsize=8)
    pylab.yticks(ypos, perclabels)
    pylab.subplot(8,1,4)
    pylab.grid(True)
    pylab.plot(epochs, mems,'-b')
    pylab.xlabel("time")
    pylab.ylabel("Memory %")
    pylab.title("Memory usage")
    pylab.xticks(xepochs, xlabels, rotation=rotation, fontsize=8)
    pylab.yticks(ypos, perclabels)
    pylab.subplot(8,1,7)
    pylab.grid(True)
    pylab.plot(epochs, cpus,'-g')
    pylab.plot(epochs, mems,'-b')
    pylab.xlabel("time")
    pylab.ylabel("%")
    pylab.title("Memory % CPU %")
    import matplotlib.font_manager
    prop = matplotlib.font_manager.FontProperties(size=8) 
    pylab.legend(("CPU %", "Memory # Megs."), prop=prop)
    pylab.xticks(xepochs, xlabels, rotation=rotation, fontsize=8)
    pylab.yticks(ypos, perclabels)
    pylab.savefig(fname)
    return fname

class UsageStore(object):
    ''' Store memory + cpu usage '''
    def __init__(self):

        newdb = os.path.exists(dbname)
        self.con = sqlite.connect(dbname)
        self.cur = self.con.cursor()
        if not newdb:
            self.cur.execute('CREATE TABLE usage (epoch float PRIMARY KEY, cpu FLOAT, memory INT)')
            self.con.commit()

    def new_cur(self):
        return self.con.cursor()

    def select(self, fields='*', start=None, stop=None, last_n_min=60):
        ''' start and stop are datetime object '''
        where = ''
        
        if start == 0:
            start = datetime.strptime("2010", "%Y")
        elif not start:
            now = datetime.now()
            delta = timedelta(minutes=last_n_min)
            start = now-delta
        
        estart = datetime2epoch(start)
        where = " where epoch > %s" %int(estart)
        
        if stop:
            estop = datetime2epoch(stop)
            where += " and epoch < %s" %int(estop)
        
        sql = 'SELECT %s FROM usage %s' %(fields, where)
        
        if start and stop:
            now = datetime.now()
            print "start < now =", start < now
            print "stop < now = ", stop < now
            print "start:", start
            print "stop:", stop
            print "now:", now

        print "sql:%s" %(sql)
        #print "now:%s: %s" %(time(), sql)
        self.cur.execute(sql)
        return self.cur.fetchall()

    def insert(self, epoch, cpuPct, memory):
        self.cur.execute('INSERT INTO usage (epoch, cpu, memory) VALUES(%s, %s, %s)' %(epoch, cpuPct, memory))
        self.con.commit()


usage = UsageStore()


def run(interval=2, verbose=True):
    from MemoryMonitor import MemoryMonitor
    memory = MemoryMonitor()
    from CpuMonitor import getCpuPerc
    from time import time, sleep
    while True  :
        cpuPct = getCpuPerc()
        memPct = memory.usagePerc()
        now = datetime.now()
        if verbose:
            print "%s \t cpu = %.2f %% memory = %.2f %%" %(datetime2str(now), cpuPct, memPct)  
        usage.insert(datetime2epoch(now), cpuPct, memPct)
        sleep(interval)    

def main():
    run()
    

if __name__ == "__main__":
    from optparse import OptionParser
    parser = OptionParser(description = __doc__)
    parser.add_option('-i', dest='interval', type=int, help='sleep interval', default=2)
    parser.add_option('--no-verbose', dest='verbose', action='store_false', help='no verbose (default True)', default=True)
    options, args = parser.parse_args()
    main(options.interval, options.verbose)
