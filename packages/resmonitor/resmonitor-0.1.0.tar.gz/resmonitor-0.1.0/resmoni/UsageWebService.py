#!/usr/bin/env python
''' Usage (CPU and Memory %) web service) '''
# to try:
# 1) firefox post_select.html
# 2) http://localhost:1111/get/* (to see graph)
# 3) http://localhost:1111/get/memory
# 4) http://localhost:1111/get/cpu
# 5) http://localhost:8888/getfrom/http://test.dev:8888/get/* or
# 6) http://192.168.0.126:8888/getfrom/x
# 7) http://192.168.0.126:8888/gethtml/post_select.html
from UsageDB import UsageStore, genPng
from UsageDB import run as usage_db_run

from retro import *

from datetime import datetime, timedelta

def getdatetime(string):
    if not isinstance(string, str):
        return None
    try:
        return datetime.strptime(string, "%Y%m%d")
    except:
        try:
            now = datetime.now()
            # get start of day
            sod = datetime.strptime(now.strftime("%Y%m%d"), "%Y%m%d")

            dt = datetime.strptime(string, "%H:%M:%S")
            delta = timedelta(hours=dt.hour, minutes=dt.minute, seconds=dt.second)
            return  sod + delta
        except:
            try:
                return datetime.strptime(string, "%Y%m%d %H:%M:%S")
            except Exception, ex:
                raise ValueError("Unknown datetime format: %s\n%s" %(string, ex))
            
class UsageWebService(Component):
    """To use this, go to <http://localhost:8888/select>"""
 
    def respond(self, data, request):
        try:
            fname = genPng(data)
            content = open(fname,'r').read()
            content_type = "image/png"
            return request.respond(content=content, contentType=content_type)
        except Exception, ex:
            print ex
            return request.respond(
                "%s" % (data)
                )
        
    @on(POST="/select")
    def select( self, request):
        fields = request.get('fields') or '*'
        start = getdatetime(request.get('start'))
        stop = getdatetime(request.get('stop'))
        u = UsageStore()
        data = u.select(fields, start, stop)
        return self.respond(data, request)

    @on(GET="/get/{fields:rest}")
    def selectall( self, request, fields="*"):
        fields = request.get('fields') or fields
        u = UsageStore()
        data = u.select(fields)
        return self.respond(data, request)

    @on(GET="/getfrom/{url:rest}")
    def getfrom( self, request, url='http://test.dev:8888/get/*'):
        getfrom = request.get('url') or url
        import urllib2
        response = urllib2.urlopen(url)
        data = eval(response.read())
        data = data.replace('http://localhost:8888/select', ull)
        try:
            fname = genPng(data)
            content = open(fname,'r').read()
            content_type = "image/png"
            return request.respond(content=content, contentType=content_type)
        except:
            return request.respond(
            "%s" % (data)
            )

    @on(GET="/gethtml/{fname:rest}")
    def gethtml( self, request, fname='post_select.html'):
        fname = request.get('fname') or fname
        import urllib2
        
        
        content = open(fname,'r').read()
        
        return request.respond(
            "%s" % (content)
            )

    @on(GET="/say/{something:rest}")
    def saySomething( self, request, something):
        return request.respond(
            "<html><body>You said: <b>%s</b></body></html>" % (something)
            )

def main():
    import subprocess
    subprocess.Popen(['usage-db'])
    run( components=[UsageWebService()])

if __name__ == "__main__": 
    # thread doesn't work UsageDB.run(...)
    #sqlite3.ProgrammingError: SQLite objects created in a thread can only be used in that same thread.The object was created in thread id -1210664768 and this is thread id -1220469872

    from optparse import OptionParser
    parser = OptionParser(description = __doc__)
    parser.add_option('-p', dest='port', type=int, help='port', default=8888)
    parser.add_option('-s', dest='sleep_sec', help='sleep # sec', default='5')
    options, args = parser.parse_args()

    import subprocess
    subprocess.Popen(['python','UsageDB.py', '--no-verbose','-i',options.sleep_sec])
    run( components=[UsageWebService()], port=options.port)
    
    
    
