#!/usr/bin/env python
# http://github.com/sebastien/retro/blob/master/README (line 249+)
from retro import *

class Main(Component):
    """To use this, go to <http://localhost:2222/get>"""
 
    @on(POST='/postfile')
    def postThis( self, request):
        file_name = request.get('name')
        file_data = request.get('fname')
        file_info = request.file('fname')
        return request.respond(
            "Received file %s, of %s bytes, with content type:%s" %
            (file_info.get("filename"),len(file_data),file_info.get("contentType")))

    @on(GET="/say/{something:rest}")
    def saySomething( self, request, something):
        return request.respond(
            "<html><body>You said: <b>%s</b></body></html>" % (something)
            )
    


if __name__ == "__main__": 
    run( components=[Main()], port=2222)
    
    
