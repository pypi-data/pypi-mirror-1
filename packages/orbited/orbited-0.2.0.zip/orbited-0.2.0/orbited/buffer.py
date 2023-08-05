
# logger = getLogger("HTTPBuffer")

class Buffer(object):
    
    def __init__(self, initial_data='', mode='index'):
        self.mode = None
        self.pos = None
        self.data = initial_data        
        self.set_mode(mode)
    
    def set_mode(self, mode):
        # No change
        if self.mode == mode:
            return
        # Switch from consume to index or initial mode is index
        elif mode == 'index':
            self.mode = 'index'
            self.pos = 0
        # Switch from index to consume
        elif mode == 'consume' and self.pos is not None:
            self.data = self.data[self.pos:]
            self.pos = None
            self.mode = 'consume'
        # initial mode is consume
        else: 
            self.mode = 'consume'
            self.pos = None
    
    def find(self, marker, i=0):
        if self.mode == 'consume':
            return self.data.find(marker, i)
        elif self.mode == 'index':
            pos =  self.data.find(marker, i + self.pos)
            if pos == -1:
                return -1
            return pos - self.pos
    
    def get_value(self):
        if self.mode == 'consume':
            return self.data
        elif self.mode == 'index':
            return self.data[self.pos:]
    
    def get_full_value(self):
        return self.data
    
    def exhaust(self):
        if self.mode == 'consume':
            self.data = ''
        elif self.mode == 'index':
            self.pos = len(self.data)
    
    def reset_position(self):
        if self.mode == 'index':
            self.pos = 0
    
    def reset(self, content = ''):
        self.data = content
        if self.mode == 'index':
            self.pos = 0
    
    def empty(self):
        if self.mode == 'consume':
            return len(self.data) == 0
        elif self.mode == 'index':
            return (len(self.data) - self.pos) == 0
    
    def move(self, i):
        if self.mode == 'consume':
            self.data = self.data[i:]
        elif self.mode == 'index':
            self.pos += i
    
    def part(self, start, end):
        if self.mode == 'consume':
            return self.data[start:end]
        elif self.mode == 'index':
            return self.data[self.pos + start: self.pos + end]
    
    def __contains__(self, data):
        if self.mode == 'consume':
            return data in self.data
        elif self.mode == 'index':
            return self.data.find(data, self.pos) != -1
    
    def __eq__(self, data):
        if self.mode == 'consume':
            return self.data == data
        elif self.mode == 'index':
            return self.data[self.pos:] == data
    
    def __len__(self):
        if self.mode == 'consume':
            return len(self.data)
        elif self.mode == 'index':
            return len(self.data) - self.pos
    
    def __get_slice__(self, start, end):
        return self.part(self, end)
    
    def __add__(self, add_data):
        if not isinstance(add_data, str):
            raise TypeError
        self.data += add_data
        return self        
    
