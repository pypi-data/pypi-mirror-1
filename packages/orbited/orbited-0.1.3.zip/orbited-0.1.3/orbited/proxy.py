import event
import socket
import io
from debug import *
def debug(arg):
    print "PROXY:: ", arg
BUFSIZ = 4096
LQUEUE_SIZ = 500


# TODO
# Check for keepalive headers. 
# Sometimes new requests come in on the same connection,
# but they shouldn't be proxied.


class ProxyDaemon(object):

    def __init__(self, port):
        print "Created Proxy@%s" % port
        self.index = 0
        self.port = port
        self.sock = io.server_socket(port)
        self.listen = event.event(self.accept_connection, 
            handle=self.sock, evtype=event.EV_READ | event.EV_PERSIST)
        self.listen.add()
        
    def accept_connection(self, event_, sock, event_type, *arg): 
        self.index+=1
        s, addr = sock.accept()
        connection = Proxy('localhost', 80, s, self.index)
        
    def start(self):
        while True:
            event.timeout(.01, idle)
            event.dispatch()      

def idle():
#    print "idle"
    return True
    
class Proxy(object):
    # TODO:
    # This proxy needs to check for multiple requests in the case of keepalive.
    # If a proxy request is made followed by an orbit request and keepalive is
    # enabled, then the orbit request will not be recognized.
    # This class should pass control back to the HTTPConnection
    def __init__(self, parent, addr, port, sock, id=-1, buffer=""):
        debug("PROXY")
        self.parent = parent
        self.id = id
        self.addr = addr
        self.port = port
        self.client_sock = sock
        self.server_sock = io.client_socket(addr, port)
        self.client_revent = event.read(self.client_sock, self.client_data_read)
        self.client_wevent = None
        self.server_revent = event.read(self.server_sock, self.server_data_read)
        self.server_wevent = None
        self.from_client_buffer = []
        self.from_server_buffer = []
        self.server_closed = False
        self.client_closed = False
        self.response = ProxyServerResponse()
        self.total_written = 0
        self.server_write_now(buffer)
        debug ("Connection %s" % self.id)
        
    def server_data_written(self):
        try:
            if not self.from_client_buffer:
                self.server_wevent = None
                return None
            item = self.from_client_buffer[0]        
            bsent = self.server_sock.send(item)
            if bsent == len(item):
                self.from_client_buffer.pop(0)
            else:
                self.from_client_buffer[0] = self.from_client_buffer[bsent:]
            return True
        except socket.error:
            self.close_server()
            return None

    def client_data_written(self):
        try:
            if not self.from_server_buffer:
                self.client_wevent = None
                if self.server_closed:
                    print "close it."
#                    self.close_client()
                return None
            item = self.from_server_buffer[0]        
            bsent = self.client_sock.send(item)
            self.total_written += bsent
            if bsent == len(item):
                self.from_server_buffer.pop(0)
            else:
                self.from_server_buffer[0] = self.from_server_buffer[bsent:]
            if self.total_written == self.response.total_length:
                self.close_server()
                self.client_revent.delete()
                self.client_wevent.delete()
                
                self.parent.proxy_complete(self)
            else:
                debug("[proxy] not yet.. %s vs. %s" % (self.total_written, self.response.total_length))
                
            return True
        except socket.error:
            self.close_client()
            return None

            
    def close_client(self,):
#        raise "What"
        debug("[ %s ] Close client" % self.id)
        self.client_closed = True
        if self.client_revent:
            self.client_revent.delete()
            self.client_revent = None
        if self.client_wevent:
            self.client_wevent.delete()
            self.client_wevent = None            
        self.client_sock.close()
        if not self.server_closed:
            self.close_server()
    def close_server(self):
        debug("[ %s ] Close server (%%s) (%%s)" % (self.id,))# self.from_server_buffer, self.from_client_buffer))
        self.server_closed = True
        if self.server_revent:
            self.server_revent.delete()
            self.server_revent = None
        if self.server_wevent:
            self.server_wevent.delete()
            self.server_wevent = None
        self.server_sock.close()
        if not self.client_wevent and not self.client_closed:
            self.close_client()
        
    def server_data_read(self):
        try:
            data = self.server_sock.recv(BUFSIZ)
            if not data:
                self.close_server()
                return None
            self.response.read(data)
            self.client_write_now(data)
            return True
        except socket.error:
            self.close_server()
            return None
            
    def client_data_read(self):
        try:
            data = self.client_sock.recv(BUFSIZ)
            if not data:
                self.close_client()
                return None
            self.server_write_now(data)
            return True
        except socket.error, ex:
            self.close_client()            
            debug("[ %s ] ERROR %s " % (self.id, ex))
            return None
#            raise
    def client_write_now(self, data):
        self.from_server_buffer.append(data)
        if not self.client_wevent:
            self.client_wevent = event.write(self.client_sock, self.client_data_written)
        
    def server_write_now(self, data):
        self.from_client_buffer.append(data)
        if not self.server_wevent:
            self.server_wevent = event.write(self.server_sock, self.server_data_written)
            

class ProxyServerResponse(object):

    def __init__(self):
        self.total_length = 0
        self.buffer = ""
        self.state = 'status'
        self.headers = {}
        self.status = None
        debug("made proxy resposne")
    def read(self, data):
        self.buffer += data
        return getattr(self, 'state_%s' % self.state)()
        
    def state_status(self):
        i = self.buffer.find('\r\n')
        if i == -1:
            return False
        self.status = self.buffer[:i]
        self.buffer = self.buffer[i+2:]
        self.total_length += i+2
        self.state  = "headers"
        debug("status: %s" % self.status)
        return self.state_headers()
        
    def state_headers(self):
        while True:
            index = self.buffer.find('\r\n')
            if index == -1:
                return False
            header = self.buffer[:index]
            self.buffer = self.buffer[index+2:]
            self.total_length += index+2
            if header == "":
                debug("headers: %s" % self.headers)
                self.state = 'completed'
                return self.state_completed()
            key, val = header.split(': ')
            self.headers[key] = val
            if key == 'Content-Length':
                self.total_length += int(val)
        
    def state_completed(self):
        debug("completed. Total Length: %s" % self.total_length)
        return self.total_length

            
if __name__ == "__main__":
    p = ProxyDaemon(8080)
    p.start()