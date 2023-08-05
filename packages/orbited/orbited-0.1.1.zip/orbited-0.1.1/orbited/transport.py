import log
import event

transports = {}

def create(conn, app):
    return transports[conn.request.transport_name](conn.key(), app)

def load_transports():
    transports.update({
        'iframe': IFrameTransport,
        'xhr': XHRTransport,
    })
        
def extract_user(req):
    if '|' in req.headers['url']:
        return req.headers['url'].split('|')        
    elif '!' in req.headers['url']:
        return req.headers['url'].split('!')


class Transport(object):
    def close(self):
        pass
    def respond(self, request):
        pass
    def accept_http_connection(self, conn):        
        pass
    def response_success(self, request, conn):
        pass
    def response_failure(self, request, conn):
        pass

class IFrameTransport(Transport):
    name = 'iframe'
    initial_data =  "HTTP/1.1 200 OK\r\n"
    initial_data += "Content-Type: text/html\r\n"
    initial_data += "Content-Length: 100000\r\n\r\n"
    initial_data += "<script>document.domain=\"%s\";</script>"
    
    def __init__(self, key, app):
        self.key = key
        self.app = app
        self.http_conn = None
        self.active = True
        
    def close(self):
        self.http_conn.close()
        self.active = False


        
    def accept_http_connection(self, conn):
        if self.http_conn is not None:
            old_conn = self.http_conn
            self.http_conn = conn
            old_conn.close()   
        else:
            self.http_conn = conn
        document_domain = self.get_domain(conn.request.headers['host'])
        self.http_conn.respond(ResponseBuffer(self.initial_data % document_domain, self))

    def get_domain(self, host):
        host = host.split(':')[0]
        subs = host.split('.')
        if len(subs) == 4:
            for sub in subs:
                try:
                    int(sub)
                except:
                    return '.'.join(subs[-2:])
            return host
        return '.'.join(subs[-2:])
    
    def respond(self, request):
        self.http_conn.respond(ResponseBuffer(request.body, self, request))
        
    def response_success(self, request, conn):
        log_recipient = "%s [ %s ]" % (str(conn.key())[1:-1], conn.addr[0])
        log.log("EVENT", "%s/%s -> %s" % (conn.addr[0], request.id, log_recipient))
        request.success(conn.key())
        
    def response_failure(self, request, conn):
        log_recipient = "%s [ %s ]" % (str(conn.key())[1:-1], conn.addr[0])
        request.error(conn.key())
    
    def expire_http_connection(self, conn):
        if conn == self.http_conn and self.active:
            del self.app.connections[self.key]            
    
class XHRTransport(Transport):
    name = 'xhr'
    timeout_delay = 30
       
    def __init__(self, key, app):
        self.key = key
        self.connections = []
        self.app = app

    def close(self):
        for conn in self.connections:
            conn.close()
        
    def accept_http_connection(self, conn):
       
        timer = event.timeout(self.timeout_delay, self.timed_out, conn)
        conn.timer = timer
        self.connections.append(conn)
        
    def expire_http_connection(self, conn):
        if conn in self.connections:
            self.connections.remove(conn)
            conn.timer.delete()
            self.cleanup()
            
    def timed_out(self, conn):
        print "TIME OUT: %s" % conn
        self.connections.remove(conn)
        conn.respond(ResponseBuffer("", self, XHRTimeoutRequest()))
            
    def respond(self, request):
        conn = self.connections.pop(0)
        conn.respond(ResponseBuffer(request.body, self, request))
        conn.timer.delete()

    def timeout_response_complete(self, conn):
        conn.close()
        
    def response_success(self, request, conn):
        if isinstance(request, XHRTimeoutRequest):
            return self.timeout_response_complete(conn)
        log_recipient = "%s [ %s ]" % (str(conn.key())[1:-1], conn.addr[0])
        log.log("EVENT", "%s/%s -> %s" % (conn.addr[0], request.id, log_recipient))
        request.success(conn.key())
        conn.close()
        self.cleanup()
        
    def response_failure(self, request, conn):
        if isinstance(request, XHRTimeoutRequest):
            return self.timeout_response_complete(conn)
        log_recipient = "%s [ %s ]" % (str(conn.key())[1:-1], conn.addr[0])
        request.error(conn.key())
        conn.close()
        self.cleanup()

    def cleanup(self):
        if not self.connections:
            del self.app.connections[self.key]
        
class XHRTimeoutRequest(object):
    pass
    
class ResponseBuffer(object):

    def __init__(self, data, transport, request=None):
        self.request = request
        self.data = data
        self.transport = transport
        
    def success(self, conn):
        if self.request:
            self.transport.response_success(self.request, conn)
        
    def failure(self, conn):
        if self.request:
            self.transport.response_failure(self.request, conn)