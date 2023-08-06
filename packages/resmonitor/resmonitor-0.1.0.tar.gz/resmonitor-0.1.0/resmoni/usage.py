 #!/usr/bin/env python

import os
import time
from datetime import datetime
try:
    import sqlite3 as sqlite
except: 
    import sqlite


dbname = 'usage.db'


class UsageStore(object):
    ''' Store memory + cpu usage '''
    def __init__(self):

        newdb = os.path.exists(dbname)
        self.con = sqlite.connect(dbname)
        self.cur = self.con.cursor()
        if not newdb:
            self.cur.execute('CREATE TABLE usage (epoch float PRIMARY KEY, cpu FLOAT, memory INT)')
            self.con.commit()

    def selectFields(self, fields="*"):
        self.cur.execute('SELECT %s FROM usage' %fields)
        return cur.fetchall()

    def insert(self, date, cpuPct, memory):
        self.cur.execute('INSERT INTO usage (epoch, cpu, memory) VALUES(%s, %s, %s)' %(date, cpuPct, memory))
        self.con.commit()


usage = UsageStore()
if __name__ == "__main__":
    
    from MemoryMonitor import MemoryMonitor
    memory = MemoryMonitor()
    from util import *
    from CpuMonitor import getCpuPerc
    from time import time
    while True  :
        cpuPct = getCpuPerc()
        mem = memory.usageInMeg()
        print "%s \t cpu = %.4f %% memory = %.2f Megs" %(getTimeStr(), cpuPct, mem)  
        usage.insert(time(), cpuPct, mem)
