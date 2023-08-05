import sys
import traceback
import StringIO
import event
from config import map as config
from http import HTTPDaemon
from log import getLogger
from orbited import transport
from orbited.exceptions import InvalidTransport
from orbited.orbit import OPDaemon
#config = config.map

logger = getLogger('Application')
access = getLogger('ACCESS')
class Application(object):
    
    def __init__(self):
        self.http = HTTPDaemon(self)
        self.op = OPDaemon(self)
        self.connections = {}
        self.requests = {}
    
    def dispatch_event(self, request):
        access.info('EVENT REQUEST\t%s/%s\t%s' % (request.connection.addr[0], request.id, request.length))
        self.requests[request.key()] = request
        for recipient in request.recipients:
            if recipient in self.connections:
                self.connections[recipient].event(request)
            else:
                access.info('EVENT FAILED\t%s/%s\t\n|---------------------- Recipient %s not Found' % (request.addr, request.id, recipient))
                request.failure(recipient)
        
        self.requests.pop(request.key())
    
    def accept_browser_connection(self, conn):
        logger.debug('entered accept_browser_connection, conn: %s' % conn)
        
        # cannot find transport
        if conn.transport not in transport.map:
            raise InvalidTransport, '%s is not a valid Orbited Transport' % conn.transport
        
        # new connection
        if conn.key() not in self.connections:
            logger.debug('New Connection %s' % (conn.key(),))
            self.connections[conn.key()] = transport.create(self, conn.transport, conn.key())
        
        # existing connection, different transport
        elif conn.transport != self.connections[conn.key()].name:
            logger.warn('Connect key exists. Switching transports %s -> %s' % (self.connections[conn.key()].name, conn.transport))
            self.connections[conn.key()].close()
            self.connections[conn.key()] = transport.create(self, conn.transport, conn.key())
        
        self.connections[conn.key()].accept_browser_connection(conn)
    
    def expire_browser_connection(self, conn):
        if conn.key() in self.connections:
            self.connections[conn.key()].expire_connection(conn)
    
    def remove_transport_connection(self, transport_conn):
        del self.connections[transport_conn.key]
    
    def start(self):
        
        def collect_toplevel_exceptions():
            return True
        
        event.timeout(1, collect_toplevel_exceptions)
        while True:
            try:
                event.dispatch()
            except KeyboardInterrupt, k:
                event.abort()
                print 'Received Ctr+c shutdown'
                sys.stdout.flush()
                sys.exit(0)
                
            except Exception, e:
                exception, instance, tb = traceback.sys.exc_info()
                if 'exceptions must be strings' in str(instance):
                    print "Error in pyevent 0.3 on ubuntu in python 2.5. See http://orbited.org/pyevent.html for details"
                    event.abort()
                    sys.exit(0)
                # TODO: Start: There is certainly a better way of doing this
                x = StringIO.StringIO()
                traceback.print_tb(tb, file=x)
                x = x.getvalue()
                relevant_line = x.split('\n')[-3]
                # End: Find a better way
                
                logger.critical('%s:%s\t%s' % (exception, instance, relevant_line))
                print x
    
