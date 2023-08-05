import os
import event
import util
from orbited import plugin
from orbited.log import getLogger

logger = getLogger('Admin')

class AdminPlugin(plugin.Plugin):
    name = 'admin'
    event_path = "/_/admin/event"
    static = os.path.join(os.path.split(__file__)[0], 'static')

    def __init__(self):
        self.data = {}
        event.timeout(1,self.send)

    def init_data(self):
        return {'bandwidth':0,'msgs':0,'users':0}

    def accept_orbited_connection(self,conn):
        user,session,location = conn.key
        location = location[3:-6]
        if location not in self.data:
            self.data[location] = self.init_data()
        self.data[location]['users'] += 1

    def close_orbited_connection(self,conn):
        user,session,location = conn.key
        location = location[3:-6]
        if location not in self.data:
            print '[error] close_orbited_connection: %s not in self.data' % (location,)
            return
        self.data[location]['users'] -= 1

    @plugin.hook(">http.http.HTTPConnection.sent_amount")
    def bandwidth_monitor(self, conn, amount):
        if conn.state == 'orbited':
            location = conn.browser_conn.location[3:-6]
            if location not in self.data:
                print '[error] close_orbited_connection: %s not in self.data' % (location,)
                return
            self.data[location]['bandwidth'] += amount
            self.data[location]['msgs'] += 1

    def clear_data(self):
        for location in self.data:
            self.data[location]['bandwidth'] = 0
            self.data[location]['msgs'] = 0

    def update_data(self):
        pass

    def send(self):
        self.update_data()
        self.broadcast()
        self.clear_data()
        return True
