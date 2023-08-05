map = {
    'orbit.port': 9000,
    'http.port': 8000,
    'admin': 1,
    'admin.port': 9001,
    'proxy': 1,
    'proxy.rules': 'prules.txt',
    'log': 0,
    'log.screen': ['access']
}

default = """orbit.port = 9000
http.port = 8000
log = 1
log.access = access.log
log.error = error.log
log.event = event.log
log.screen = access, error
"""

def update(**kwargs):
    map.update(kwargs)
    return True

def load(filename):
    try:
        f = open(filename)
        data = f.read()
        lines = data.split('\n')
        
    except IOError:    
        print filename, "could not be found. Using default configuration"
        lines = default.split('\n')
        
        
        
    for line in lines:
        if '=' not in line:
            continue
        line = line.replace(' =', '=')
        line = line.replace('= ', '=')
        key, value = line.split('=')
        map[key] = value.strip()
    map['log.screen'] = [ i.strip().upper() for i in map['log.screen'].split(',') ]
    return True
    