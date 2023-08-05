from daemon import OrbitDaemon
from http import HTTPDaemon
import event
from debug import *
import log
from config import map as config
from admin import AdminApp
import transport

#config = config.map
"""
app:    
    stores all requests
    executes requests
    replies to requests
   
   
daemon:
    accepts socket connections. creates connection objects
    
connection:
    reads data and creates new requests as needed
request:
    processes read data and stores info about a request
    
"""

class App(object):

    def __init__(self):
        self.requests = dict()
        self.connections = dict()
        log.create(self)
        self.log = log.log
        self.admin = AdminApp(self, int(config['admin.port']))
        self.daemon = OrbitDaemon(self, self.log, int(config['orbit.port']))
#        if int(config['proxy']):
        self.http = HTTPDaemon(self, self.log, int(config['http.port']), [])
        
    def accept_orbit_request(self, request):
        self.log("ACCESS", "ORBIT\t%s/%s\t%s" % (request.connection.addr[0], request.id, request.length))
        self.requests[request.key()] = request
        self.dispatch_request(request)

        
    def dispatch_request(self, request):
        for recipient in request.recipients:
            if recipient in self.connections:
                self.connections[recipient].respond(request)
            else:
                self.log("ERROR", "ORBIT\t%s/%s\tRecipient not Found" % (request.connection.addr[0], request.id))
                request.error(recipient)
                    
        self.requests.pop(request.key())
        
    def accept_http_connection(self, connection):
        if connection.key() not in self.connections:
            self.connections[connection.key()] = transport.create(connection)        
        self.connections[connection.key()].accept_http_connection(connection)
#            self.log('close_http_connection', self.connections[connection.key()]) 
#            self.connections[connection.key()].close()

    def expire_http_connection(self, connection):
        self.connections.pop(connection.key())
        
    def start(self):
    
        def idle():
            return True
            
        while True:
            event.timeout(.1, idle)
            event.dispatch()
            
            
if __name__ == "__main__":
    a = App()
    a.start()
    