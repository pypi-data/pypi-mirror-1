from twisted.internet import reactor
from orbited import logging
from orbited.transports.longpoll import LongPollingTransport

class CometP(LongPollingTransport):
    logger = logging.get_logger('orbited.transports.longpoll.CometP')

    def opened(self):
        self.totalBytes = 0
        self.close_timer = reactor.callLater(30, self.triggerCloseTimeout)
        self.request.setHeader('cache-control', 'no-cache, must-revalidate')

    def write(self, packets):
        self.logger.debug('write %r' % packets)
        payload = self.encode(packets)
        self.logger.debug('WRITE ' + payload)
        self.request.write(payload)
        self.close()

    def encode(self, packets):
        jsonp = self.request.args.get('jsonp', ['defaultCallback'])[0]
        return "%s(%s)"%(jsonp, packets)
