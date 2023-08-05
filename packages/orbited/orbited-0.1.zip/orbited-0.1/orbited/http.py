import io
import event
import random
import transport
from debug import *
from proxy import Proxy
class ProxyChecker(object):
    def __init__(self, rules):
        pass        
        
    def __call__(self, url):
        if '|' in url or '!' in url:
            return False
        return ("localhost", 4700)
        

class HTTPDaemon(object):
    def __init__(self, app, log, port, rules):
        log("startup", "Created http@%s" % port)
        self.log = log
        sock = io.server_socket(port)
        self.app = app
        self.listen = event.event(self.accept_connection, handle=sock, evtype=event.EV_READ | event.EV_PERSIST)
        self.listen.add()
        self.proxy_checker = ProxyChecker(rules)
        
        
    def accept_connection(self, ev, sock, event_type, *arg):
        sock, addr = sock.accept()
#        self.log("ACCESS", "http", *addr)

        HTTPConnection(self.app, self.log, self.proxy_checker, sock, addr)
        
        
class HTTPConnection(object):
    def __init__(self, app, log, proxy_checker, sock, addr):
        self.sock = sock
        self.addr = addr
        self.app = app
        self.log = log
        self.revent = event.read(sock, self.read_ready)
        self.wevent = None
        self.buffer = ""
        self.write_buffer = ""
        self.request = HTTPRequest(proxy_checker)
        self.proxy_checker = proxy_checker
        self.events = []
        self.current_response = None


    def close(self):
        self.sock.close()
        if self.revent:
            self.revent.delete()
            self.revent = None
        if self.wevent:
            self.wevent.delete()
            self.wevent = None
        self.app.expire_http_connection(self)
            
    def write_ready(self):
        if not self.write_buffer:
            if self.current_response:
                self.current_response.success(self)
                self.current_response = None
            if not self.events:
                self.wevent = None
                return None
            self.current_response = self.events.pop(0)
            self.write_buffer = self.current_response.data        
        try:
            bsent = self.sock.send(self.write_buffer)
            debug("http sent: %s" % self.write_buffer[:bsent])
            self.write_buffer = self.write_buffer[bsent:]
            return True
        except io.socket.error:
            self.current_response.failure(self)
            self.close()
            return None

    def respond(self, response):
        self.events.append(response)
        if not self.wevent:
            self.wevent = event.write(self.sock, self.write_ready)

            
    def read_ready(self):
        try:
            data = self.sock.recv(io.BUFFER_SIZE)
            if not data:
                self.close()
                return None
            return self.read(data)
        except io.socket.error:
            self.close()
            return None

    def read(self, data):
        proxy_info =  self.request.read(data)
        if proxy_info:
            addr, port = proxy_info
            self.log("ACCESS", "PROXY\t%s -> http://%s:%s" % (self.request.headers['url'],addr, port))
            a = self.request.action + "\r\n" + "\r\n".join([ ": ".join(i) for i in self.request.headers.items()]) + "\r\n\r\n"
            #debug("buf: %s" % a)
            Proxy(addr, port, self.sock, buffer=a)
#            Proxy(addr, port, self.sock,buffer)
            self.revent.delete()
            self.revent = None
            return None
        elif self.request.complete:
            self.log("ACCESS", "HTTP\t(%s, %s, %s)" % self.key())        
            self.app.accept_http_connection(self)
            return None
        return True
        
    def key(self):
        return self.request.key()

        

class HTTPRequest(object):
    def __init__(self):
        print "yoho"
        
    def __init__(self, proxy_checker):
        self.buffer = ""
        self.state = "action"
        self.headers = {}
        self.proxy_checker = proxy_checker
        self.complete = False
        
    def read(self, data):
        self.buffer += data
        return self.process()
        
    def process(self):
        return getattr(self, 'state_%s' % self.state)()
        
    def state_action(self):
        if '\r\n' not in self.buffer:
            return
        i = self.buffer.find('\r\n')
        self.action = self.buffer[:i]
        debug("action: %s" % self.action)
        self.buffer = self.buffer[i+2:]
        self.state = "headers"
        self.headers['url'] = self.action.split(' ')[1]
        return self.state_headers()
        
    def state_headers(self):
        while True:
            index = self.buffer.find('\r\n')
#            debug("%s == %s ? " % (index, end))
            if index == -1:
                break;
            if index == 0:
                self.buffer = self.buffer[2:]
                self.state="completed"
                return self.state_completed()
            debug("line: %s" % self.buffer[:index])
            debug("split: %s" % self.buffer[:index].split(': '))
            key, value = self.buffer[:index].split(': ')
            self.headers[key.lower()] = value
            self.buffer = self.buffer[index+2:]

    def state_completed(self):
        target_addr = self.proxy_checker(self.headers['url'])
        if target_addr:
            debug("ackblech")
            return target_addr 
        else:
            
            self.location, self.user_id = transport.extract_user(self)
            #TODO: use real sessions
            self.session_id = '0'
            self.complete = True
            debug("completed")
            
    def key(self):
        return self.user_id, self.session_id, self.location
        
#    def state_body():
#        if len(self.buffer) < int(self.headers['content-length']):
#            return
#        self.body = self.buffer[:self.headers['content-length']
        # TODO: Exception if there's more data. when would this happen?
#        return True
        
#            if extra:
#                self.state = "body"
#            self.buffer = extra
#        elif state == "body":
#            self.buffer += data
#            if len(self.buffer) >= request['content-length']:

    