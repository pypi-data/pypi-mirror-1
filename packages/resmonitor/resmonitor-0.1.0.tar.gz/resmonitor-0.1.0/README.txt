MachineUsageWebService: a simple cpu & memory webservice
==================================

http://localhost:8888/get/* (get a png graph)
http://localhost:8888/get/cpu (get cpu)
http://localhost:8888/get/memory
http://localhost:8888/get/epoch,cpu,memory

Licence
-------
GPLv3

Dependencies:
-------------
retro http://github.com/sebastien/retro
sqlite

Instructions
------------
install it:
wget http://github.com/sebastien/retro/tarball/master
easy_install sebastien-retro-*.tar.gz
easy_install sqlite
easy_intall MachineUsageWebService.tgz

start it:

1) Webservice
python UsageWebService.py &

or
python CpuMonitor.py
python MemoryMonitor.py
python UsageDB.py

2) server datavisualisation from another server 
http://localhost:8888/getfrom/http://test:8888/get/


