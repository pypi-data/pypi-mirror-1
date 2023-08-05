import io
import event
from debug import *
from request import *

class OrbitDaemon(object):

    def __init__(self, app, log, port):
        log("startup", "Created Orbit@%s" % port)
        self.log = log
        self.index = 0
        self.port = port
        self.app = app
        self.sock = io.server_socket(port)
        self.listen = event.event(self.accept_connection, 
            handle=self.sock, evtype=event.EV_READ | event.EV_PERSIST)
        self.listen.add()
        
    def accept_connection(self, event_, sock, event_type, *arg):
        self.index+=1
        connection = OrbitConnection(sock.accept(), self.index, self.app, self.log)
        
        
class OrbitConnection(object):
    def __init__(self, (sock, addr), id, app, log):
        self.log = log
        debug("Accepting Orbit Connection [id: %s ] from %s on port %s" % ((id,) + addr))
        self.id = id
        self.app = app
        self.addr = addr
        self.sock = sock
        self.revent = event.read(sock, self.read_data)
        self.wevent = None
        self.response_queue = []
        self.write_buffer = ""
        self.request = Request(self, self.log)
        
    def close(self):
        debug("Closing Orbit Connection [id: %s ] from %s on port %s" % ((self.id,) + self.addr))
        self.wevent = None
        self.revent = None
        self.sock.close()
        
        
        
    def read_data(self):
        try:
            data = self.sock.recv(io.BUFFER_SIZE)
        except:
            data = None
        if not data:
            self.close()
            return None
        try:
            self.request.read_data(data)
        except RequestComplete, ex:
            debug("Request finished. Start a new one")
            self.app.accept_orbit_request(self.request)
            self.request = Request(self, self.log, ex.leftover_buffer)   
            while True:
                try:
                    self.request.process()
                    break
                except RequestComplete, ex:
                    self.app.accept_orbit_request(self.request)
                    self.request = Request(self, self.log, ex.leftover_buffer)
        return True
        
    def write_data(self):
        try:
            bsent = self.sock.send(self.write_buffer)
            print "wrote:\n======\n%s" % self.write_buffer[:bsent]
            self.write_buffer = self.write_buffer[bsent:]
            return self.write_next()
        except io.socket.error:
            return None
            
    def write_next(self):
        if not self.write_buffer:
            if not self.response_queue:
                self.wevent = None
                return None
            else:
                self.write_buffer = self.response_queue.pop(0)
                if not self.wevent:
                    self.wevent = event.write(self.sock, self.write_data)
                return True
                    
    def respond(self, response):
        self.response_queue.append(response)
        self.write_next()
        
