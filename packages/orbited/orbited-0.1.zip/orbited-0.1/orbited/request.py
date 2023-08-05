from debug import *
import random
END = '|'#'\0'
END_LINE = '\\'#'\1'
SEP_ARG = '-'#'\2'

class RequestComplete(Exception):

    def __init__(self, leftover_buffer):
        self.leftover_buffer = leftover_buffer
        Exception.__init__(self)


    
class Request(object):

    def __init__(self, connection, log, buffer=""):
        self.log = log
        self.connection = connection
        self.version = None
        self.type = None
        self.id = None
        self.recipients = []
        self.replies = {}
        self.state = "version"
        self.buffer = buffer
        
    def key(self):
        if not self.id:
            raise "NoKey"        
        return self.connection.id, self.id
        
        
    def read_data(self, data):
        print "read:\n=====\n %s" % data
        self.buffer += data
        self.process()
            
    def process(self):
        if self.state == 'body':
            if len(self.buffer) < self.length:
                return
            self.body = self.buffer[:self.length]
            debug("body: %s" % self.body)
            self.buffer = self.buffer[self.length:]
            raise RequestComplete(self.buffer)
            
        if '\r\n' in self.buffer:
            i = self.buffer.find('\r\n')
            line = self.buffer[:i]
            self.buffer = self.buffer[i+2:]
            getattr(self, 'state_%s' % self.state)(line)
            self.process()
            
        
    def state_version(self, line):
        debug("version: %s" % line)
        self.version = line
        self.state = 'type'
        
    def state_type(self, line):
        debug("type: %s" % line)
        self.type = line
        self.state = "headers"
        
    def state_headers(self, line):
        debug("header: %s" % line)
        if line == '':
            self.state = 'body'
            return
        name, content = line.split(': ')
        name = name.lower()
        if name == 'id':
            self.id = content
        elif name == 'recipient':
            self.recipients.append(tuple(content.split(', ')))
        elif name == 'length':
            self.length = int(content)

    def error(self, recipient_key):
        recipient = "(%s, %s, %s)" % recipient_key
        self.replies[recipient] = 0
        if len(self.replies.keys()) == len(self.recipients):
            self.reply()
            
    def success(self, recipient_key):
        recipient = "(%s, %s, %s)" % recipient_key
        self.replies[recipient] = 1
        if len(self.replies.keys()) == len(self.recipients):
            self.reply()

    def reply(self):
        if len(self.recipients) == sum(self.replies.values()):
            self.reply_success()
        else:
            self.reply_failure()
    
    def reply_success(self):
        response = "Success\r\nid: %s\r\n\r\n" % self.id
        self.connection.respond(response)
        
    def reply_failure(self):
        response = "Failure\r\nid: %s\r\nmsg: Failed to reach one or more recipients\r\n" % self.id
        for recipient, success in self.replies.items():
            if not success:
                response += "recipient: %s\r\n" % (recipient,)
        response += "\r\n"
        self.connection.respond(response)
        