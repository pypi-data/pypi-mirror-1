from config import map as config
from datetime import datetime

global log
log = None
class Logger(object):
    
    def __init__(self, app):
        self.app = app
        self.process = self._process
        self.events = []
        self.access = open(config["log.access"], "a")
        self.error = open(config["log.error"], "a")
        self.event = open(config["log.event"], "a")
        
    def __call__(self, *args):
        self.process(*args)
        
    def _process(self, context, msg, severity=5):
        if context == "startup":
            print msg#[0]
        file = None
        if context == "ACCESS":
            file = self.access
        if context == "ERROR":
            file = self.error
        if context == "EVENT":
            file = self.event
        if not file:
            return
            
        time = str(datetime.now())[:-3]
        out = "\t".join([time, context, msg])
        file.write('%s\n' % out)
        if context in config['log.screen']:
            print out
        file.flush()
    
def create(app):
    global log
    log = Logger(app)
    