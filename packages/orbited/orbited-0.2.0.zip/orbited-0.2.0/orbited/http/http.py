import cgi
import event
from router import StaticDestination, ProxyDestination, OrbitedDestination, \
                   PluginDestination, OrbitedEventRequest, router
from proxy import Proxy, ProxyComplete
from orbited.buffer import Buffer
#from orbited.orbit import HTTPOrbitRequest
from content import HTTPContent, HTTPClose, HTTPRequestComplete
from orbited.log import getLogger
from orbited.config import map as config
from orbited import io
from orbited.exceptions import HTTPProtocolError, OrbitedHTTPError
access = getLogger('ACCESS')                   


class HTTPConnection(object):
    logger = getLogger('HTTPConnection')
    id = 0
#    import logging
#    logger.setLevel(logging.DEBUG)
    def __init__(self, daemon, sock, addr):
        HTTPConnection.id += 1
        self.id = HTTPConnection.id
        self.logger.debug('Creating HTTPConnection with id %s' % self.id)
        self.daemon = daemon
        self.app = daemon.app
        self.sock = sock
        self.addr, self.local_port = addr
        self.new_request()
        self.proxy = None
    
    def new_request(self):
        self.browser_conn = None
        self.revent = event.read(self.sock, self.read_ready)
        self.wevent = None
        self.request = HTTPRequest(self)
        self.write_buffer = Buffer(mode='consume')
        self.buffer = Buffer()
        self.response_queue = []
        self.current_response = None
        self.state = 'reading'
    
    def proxy_completed(self):
        if self.proxy.keepalive:
            self.proxy.completed()
            self.new_request()
        else:
            self.proxy.close()
            self.close()
    
    def read_ready(self):
        try:
            data = self.sock.recv(io.BUFFER_SIZE)
            if not data:
                self.logger.debug('Read empty string... call self.close()')
                # self.close()
                return None
            return self.read(data)
        except io.socket.error:
            self.close()
            return None
    
    def read(self, data):
        # self.logger.debug('entered read, data: %s' % (data[:4] + '...'))
        self.logger.debug('state: %s' % self.state)
        if self.state != 'reading':
            self.logger.debug('raising something...')
            raise HTTPProtocolError, 'Unexpected data: %s' % data
        self.buffer += data
        
        if self.request.process():
            return self.dispatch()
        # Continue reading...
        return True
    
    def dispatch(self):
        action = router(self.request)
        if isinstance(action, ProxyDestination):
            access.info('ACCESS\tPROXY\t%s -> %s:%s [ %s ]' % (self.request.url, action.addr, action.port, self.addr))
            self.state = 'proxy'
            if not self.proxy:
                self.proxy = Proxy(self)
            # Give proxy the whole buffer
            self.buffer.reset_position()
            self.proxy.proxy_request(action.addr, action.port)
            return None
        
        elif isinstance(action, StaticDestination):
            access.info('ACCESS\tSTATIC\t%s' % action.url)
            self.state = 'static'
            self.write(HTTPContent(action.content))
            self.write(HTTPClose())
            return None
        
        elif isinstance(action, PluginDestination):
            access.info('ACCESS\tPlugin (%s)\t%s' % (action.plugin.name, action.url))
            self.state = "plugin"
            action.plugin.dispatch(self.request)
        
        elif isinstance(action, OrbitedDestination):
            conn = BrowserConnection(self.request)
            self.browser_conn = conn
            access.info('ACCESS\tORBITED\\%s\t%s' % (conn.transport, conn.recipient()))
            self.state = 'orbited'
            self.app.accept_browser_connection(conn)
            return None
        
        elif isinstance(action, OrbitedEventRequest):
            self.state = 'orbitrequest'
            req = HTTPEventRequest(self.request)
            access.info('ACCESS\tHTTP-OP\t\%s\t%s' % (req.id, req.addr))
            self.app.accept_orbit_request(HTTPOrbitRequest(self.request))
            # return True # TODO: allow OP over HTTP
    
    
    def write(self, content):
        self.response_queue.append(content)
        if not self.wevent:
            # TODO: creating a write event if the socket is closed causes a
            #       big crash. fix it.
            self.wevent = event.write(self.sock, self.write_ready)
            self.current_response = self.response_queue.pop(0)
            self.write_buffer.reset(self.current_response.content())
    
    def write_ready(self):
        self.logger.debug('entered write_ready')
        if self.write_buffer.empty():
            self.logger.debug('send completed for %s' % self.current_response)
            self.current_response.success(self)        
            self.current_response = None
            if not self.response_queue:
                self.wevent = None
                return None
            self.current_response = self.response_queue.pop(0)
            self.logger.debug('new response: %s' % self.current_response)
            if isinstance(self.current_response, ProxyComplete):
                self.logger.debug('proxy complete')
                self.current_response = None
                self.proxy_completed()
                if not self.response_queue:
                    return None
                self.current_response = self.response_queue.pop(0)
            if isinstance(self.current_response, HTTPRequestComplete):
                self.logger.debug('request complete')
                self.current_response = None
                self.new_request()
                return None
            if isinstance(self.current_response, HTTPClose):
                self.logger.debug('write_ready recieved HTTPClose')
                self.current_response = None
                self.close()
                return None
            else:
                self.write_buffer.reset(self.current_response.content())
        
        # Do actual writing here
        try:
            bsent = self.sock.send(self.write_buffer.get_value())
            # Bandwith hook
            self.sent_amount(bsent)
            self.logger.debug('SEND: %s' % self.write_buffer.part(0,bsent))
            self.write_buffer.move(bsent)
            self.logger.debug('write_buffer: return True')
            # self.write_buffer = self.write_buffer[bsent:]
            return True
        except io.socket.error, msg:
            self.logger.debug('io.socket.error: %s' % msg)
            self.close(reason=msg)
            return None
    
    # Bandwith hook
    def sent_amount(self, amount):
        pass
    
    def close(self, reason=''):
        self.logger.debug('entered close')
        if self.current_response:
            self.current_response.failure(self, reason)
        for response in self.response_queue:
            response.failure(self, reason)
        if self.wevent:
            self.wevent.delete()
            self.wevent = None
        if self.revent:
            self.revent.delete()
            self.revent = None
        self.sock.close()
        if self.state == 'orbited':
            self.app.expire_browser_connection(self.browser_conn)
    

class HTTPRequest(object):
    logger = getLogger('HTTPRequest')
    
    def __init__(self, conn):
        self.conn = conn
        self.state = 'action'
        self.headers = {}
        self.complete = False
        self.cookies = {}
        self.form = {}
    
    def process(self):
        return getattr(self, 'state_%s' % self.state)()        
    
    def state_action(self):
        if '\r\n' not in self.conn.buffer:
            return False
        i = self.conn.buffer.find('\r\n')
        self.action = self.conn.buffer.part(0,i)
        self.type, self.url, self.protocol = self.conn.buffer.part(0,i).split(' ')
        self.type = self.type.lower()
        self.protocol = self.protocol.lower()
        self.conn.buffer.move(i+2)
        self.state = 'headers'
        return self.state_headers()
    
    def state_headers(self):
        while True:
            index = self.conn.buffer.find('\r\n')
            if index == -1:
                return False
            if index == 0:
                self.conn.buffer.move(2)
                self.state='body'
                return self.state_body()
            key, value = self.conn.buffer.part(0, index).split(': ')
            self.headers[key.lower()] = value
            self.conn.buffer.move(index+2)
    
    def state_body(self):
        if self.type == 'get':
            if '?' in self.url:
                self.url, self.qs = self.url.split('?', 1)
            else:
                self.qs = ''            
            self.state = 'completed'
            return self.state_completed()
        elif self.type == 'post':
            if not hasattr(self, 'content_length'):
                if 'content-length' not in self.headers:    
                    raise HTTPProtocolError, 'No Content-Length header specified'
                try:
                    self.content_length = int(self.headers['content-length'])
                except ValueError:
                    raise HTTPProtocolError, 'Invalid Content-Length: %s' % self.headers[content-length]
            if len(self.conn.buffer) < self.content_length:
                return False
            self.qs = self.conn.buffer.part(0, self.content_length)
            self.conn.buffer.move(self.content_length)
            self.state = 'completed'
            return self.state_completed()
    
    def state_completed(self):
        if 'cookie' in self.headers:
            self.logger.warn(self.headers['cookie']) # LOG IT!
            for key, val in [ i.split('=') for i in self.headers['cookie'].split(';') ]:
                self.cookies[key] = val
        for key, val in cgi.parse_qsl(self.qs):
            self.form[key] = val
        return True
    
    def key(self):
        return self.user_id, self.session_id, self.location
    
    def respond(self, response):
        self.conn.write(response)

    def close(self):
        self.conn.close()        
        
class BrowserConnection(object):
    id = 0
    logger = getLogger('BrowserConnection')
    def __init__(self, request):
        BrowserConnection.id += 1
        self.id = BrowserConnection.id
        self.request = request
        if 'user' not in request.form:
            raise OrbitedHTTPError, 'user ID must be specified in the GET or POST request'
        
        self.user_id = request.form['user']
        self.location = request.url
        # session key is either in form or cookies
        self.session_key = request.form.get('session', None)
        if not self.session_key:
            self.logger.debug('session not found in form')
            self.seession_key = request.cookies.get('session', None)
            if not self.session_key:
                self.logger.debug('session not foun in cookie')
                self.logger.debug('choosing default session key')
                self.session_key = config['[global]']['session.default_key']
        else:
            self.logger.debug('session key found in form')
        self.transport = request.form.get('transport', config['[transport]']['default'])
        self.addr = self.request.conn.addr
    
    def respond(self, response):
        self.logger.debug('entered respond()')
        self.request.respond(response)
    
    def close(self):
        self.logger.debug('entered close()')
        self.request.close()
    
    def key(self):
        return self.user_id, self.session_key, self.location
    
    def recipient(self):
        return '"%s, %s, %s" [%s]' % (self.user_id, self.session_key, self.location, self.addr)
    
