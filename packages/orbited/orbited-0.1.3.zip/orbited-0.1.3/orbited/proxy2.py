import io
import event
from debug import *
class Proxy(object):
    def __str__(self):
        return "<Proxy %s>" % self.id
        
    def debug(self, data):
        pass
        return
        print "%s %s" % (self, data)
        
    def __init__(self, parent, addr, port, sock, buffer="", keepalive=0, id="0"):
        self.parent = parent
        self.keepalive = keepalive
        self.addr = addr
        self.port = port
        self.id = id
        self.setup(sock)
        self.server_write_now(buffer)
        self.state = "proxying"
        
    def setup(self, sock):
        self.client_sock = sock
        if not hasattr(self, 'server_sock'):
            self.server_sock = io.client_socket(self.addr, self.port)
        self.client_wevent = None
        self.client_revent = event.read(self.client_sock, self.client_read_ready)
        self.server_wevent = None
        if not hasattr(self, 'server_revent') or not self.server_revent:
            self.server_revent = event.read(self.server_sock, self.server_read_ready)        
        self.server_closed = False
        self.client_closed = False
        
        self.from_client_buffer = ""
        self.from_server_buffer = ""
        
        self.server_response = ProxyServerResponse(self.debug)
        self.total_written_to_client = 0

        
    def next_request(self, sock, buffer):
        self.setup(sock)
        self.state = "proxying"
        self.server_write_now(buffer)
        
    def request_complete(self):
        if self.keepalive == 0:
            self.debug("NO KEEPALIVE")
            self.close_server()
            self.close_client()
            self.parent.proxy_complete2(self, True)
        else:
            self.debug("We Got Keepalive!")
            self.state = "waiting"
            self.close_client(False)
            self.parent.proxy_complete(self)


    def close_server(self, close_sock=True):
        if self.server_wevent:
            self.server_wevent.delete()
        if self.server_revent:
            self.server_revent.delete()
        if close_sock:
            self.server_sock.close()
        
    def close_client(self,close_sock=True):
        if self.client_wevent:
            self.client_wevent.delete()
        if self.client_revent:
            self.client_revent.delete()
        if close_sock:
            self.client_sock.close()
        
        
    def server_has_closed(self, err=False):
        self.debug("server closed... %s" %err)
        self.close_server()
        if self.state == "waiting":
            self.parent.proxy_expired(self)
        
    def client_has_closed(self, err=False):
        self.debug("client closed... %s" % err)
        self.close_client()
        self.parent.proxy_complete2(self, True)
        
    def server_write_ready(self):
        try:
            if not self.from_client_buffer:
                self.server_wevent = None
                return None
            bsent = self.server_sock.send(self.from_client_buffer)
            self.from_client_buffer = self.from_client_buffer[bsent:]
            return True
        except io.socket.error:
            self.server_has_closed(err=True)
        
    def client_write_ready(self):
        try:
            if not self.from_server_buffer:
                self.debug("FINISHED BUFFER")
                self.client_wevent = None                
                return None
            if self.total:
                if len(self.from_server_buffer) + self.total_written_to_client > self.total:
                    # When would this happen?
                    overflow = self.from_server_buffer[:bsent - self.total_written_to_client]
            bsent = self.client_sock.send(self.from_server_buffer)
            self.total_written_to_client += bsent
            self.from_server_buffer = self.from_server_buffer[bsent:]
            if self.total == self.total_written_to_client:
                self.request_complete()
                return None
            return True
        except io.socket.error, err:
            self.debug("err: %s" % err)
            self.debug("self.from_server_buffer: %s" % len(self.from_server_buffer))
            self.debug("total_written_to_client: %s" % self.total_written_to_client)
            self.debug("total: %s" % self.total)
            self.client_has_closed(err=True)
            
        
    def server_read_ready(self):
        try:
            data = self.server_sock.recv(io.BUFFER_SIZE)
            if not data:
                self.server_has_closed()
                return None
            self.debug("server_read: %s" % len(data))
            self.total = self.server_response.read(data)            
            self.client_write_now(data)
            return True
            
        except io.socket.error:
            self.server_has_closed(err=True)
            
    def client_read_ready(self):
        try:
            data = self.client_sock.recv(io.BUFFER_SIZE)
            if not data:
                self.client_has_closed()
                return None
#            self.debug("client_read\n===\n%s\n==========" % data)
            self.server_write_now(data)
            return True
        except io.socket.error:
            self.client_has_closed(err=True)
            return None
            
    def client_write_now(self, data):
        self.from_server_buffer += data
        self.debug("writing: %s" % len(self.from_server_buffer))
        if not self.client_wevent:
            self.client_wevent = event.write(self.client_sock, self.client_write_ready)
        else:
            print "pending event: %s" % self.client_wevent.pending()
    def server_write_now(self, data):
        self.from_client_buffer += data
        if not self.server_wevent:
            self.server_wevent = event.write(self.server_sock, self.server_write_ready)



class ProxyServerResponse(object):

    def __init__(self, debug):
        self.debug = debug
        self.total_length = 0
        self.buffer = ""
        self.state = 'status'
        self.headers = {}
        self.status = None
        self.debug("made proxy resposne")
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
        self.debug("status: %s" % self.status)
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
                self.debug("headers: %s" % self.headers)
                self.state = 'completed'
                return self.state_completed()
            key, val = header.split(': ')
            self.headers[key] = val
            if key == 'Content-Length':
                self.total_length += int(val)
        
    def state_completed(self):
        self.complete = True
        return self.total_length
            