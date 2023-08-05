import logging
import pkg_resources
import orbited
from orbited.log import getLogger
from orbited.http.router import router
from orbited.util import formatBlock
from orbited.http.content import HTTPClose, HTTPContent, HTTPRequestComplete

class Loader(object):
    logger = getLogger("Plugins")
    # logger.setLevel(logging.DEBUG)
    
    def __init__(self):
        self.plugins = {}
        self.hooks = {}
        self.hook_functions = {}
        router.register_plugin_loader(self)
    
    def load(self):
        for plugin_entry in pkg_resources.iter_entry_points('orbited.plugins'):
            self.logger.info("Loading plugin: %s" % plugin_entry)
            plugin = plugin_entry.load()
            self.plugins[plugin.name] = plugin()
        
        for plugin in self.plugins.values():
            router.register_plugin(plugin)
            for source, target in plugin.hooks.items():
                source_name = source[1:]
                direction = source[0]
                if source_name not in self.hooks:
                    self.hooks[source_name] = {
                        '>': [],
                        '<': []
                    }
                try:
                    self.hooks[source_name][direction].append((plugin, getattr(plugin, target)))
                except AttributeError:
                    self.logger.critical("Plugin %s: has no attribute: %s" % (plugin, target))
                except KeyError :
                    self.logger.critical("Plugin %s: Invalid direction '%s'" % (plugin, direction))
                    raise Exception
        
        for name in self.hooks.keys():
            try:
                self.hook_functions[name] = self.load_target(name)
            except:
                self.logger.critical("Plugin: %s, Invalid Hook: %s" % (self.hooks[name], name))
                raise
    
    def import_target(self, name):
        cur = orbited
        parent = None
        func = None
        pieces = name.split('.')
        for i in range(len(pieces)):
            prev = '.'.join(pieces[:i])
            piece = pieces[i]
            val = getattr(cur, piece, None)
            if val is None:
                prev = 'orbited.' + '.'.join(pieces[:i+1])
                
                __import__(prev)
                val = getattr(cur, piece)
            if i == len(pieces)-1:
                func = val
            if i == len(pieces)-2:
                parent = val
            cur = val
        return parent, func, pieces[-1]
    
    def load_target(self, name):
        # Get the function
        parent, orig_func, orig_name = self.import_target(name)
        
        def hook_wrapper(*args, **kwargs):
            for plugin, in_hook in self.hooks[name]['>']:
                try:
                    in_hook(*args, **kwargs)
                except Exception:
                    self.logger.error(exc_info=True)
            data = orig_func(*args, **kwargs)
            for plugin, out_hook in self.hooks[name]['<']:
                try:
                    out_hook(data)
                except Exception:
                    self.logger.error(exc_info=True)
            return data
        
        self.logger.debug("setting... was: " + str(getattr(parent, orig_name)))
        setattr(parent, orig_name, hook_wrapper)
        self.logger.debug("set.. is: " + str(getattr(parent, orig_name)))
    
    def hook_in(self, name, *args, **kwargs):
        pass
    
    def hook_out(self, name, *args, **kwargs):
        pass
    

loader = Loader()

def load():
    loader.load()


class PluginMeta(type):
    def __init__(cls, name, bases, dct):
        if name == "Plugin":
            return
        if 'name' not in dct:
            raise Exception("plugin must have a name.")
        name = dct['name']
        if 'routing' not in dct:
            routing = {
                'base': '/_/%s' % name,
                'ORBITED': [ '/event' ],
            }
            if 'static' in dct:
                routing['static'] = { 
                    '/static': dct['static']
                }
            cls.routing = routing
        dynamic = []
        hooks = {}
        for key, val in dct.items():
            if hasattr(val, 'dynamic') and val.dynamic == True:
                dynamic.append(key)
            if hasattr(val, 'hook'):
                hooks[val.hook] = key
                
        cls._dynamic = dynamic
        cls.hooks = hooks
    

def dynamic(func):
    func.dynamic = True    
    return func

def hook(target):
    def dec(func):
        func.hook = target
        return func
    
    return dec

class RawPlugin(object):
    pass


class Plugin(RawPlugin):
    __metaclass__ = PluginMeta
    
    # Default Hooks
    def orbited_connect(self, conn):
        pass
    
    def orbited_disconnect(self, conn):
        pass
    
    def dispatch(self, request):
        loc = request.url[len(self.routing['base']):]
        if len(loc) > 0 and loc[0] == "/":
            loc = loc[1:]
        
        if loc == "":
            target = self.routing['base'] + '/static/index.html'
            if target in router.static:                
                request.respond(HTTPContent(router.static[target]))
                request.respond(HTTPClose())
                return
            # index
        elif loc in self._dynamic:
            response = PluginHTTPResponse(request)
            getattr(self, loc)(request, response)
            return response.render()            
        
        # 404
        headers = formatBlock('''
                HTTP/1.x 404 Not Found
                Content-Length: %s
                Content-Type: text/html
                Server: Orbited 0.2.0
            ''') + '\r\n\r\n'
        body = "Requested resource was not found"
        request.respond(HTTPContent(headers % (len(body)) + body))
        request.respond(HTTPRequestComplete())    
    

class PluginHTTPResponse(object):
    
    def __init__(self, request):
        self.request = request
        self.headers = {}
        self.buffer = []
    
    def __setitem__(self, key, val):
        self.headers[key] = val
    
    def __getitem__(self, key):
        return self.headers[key]
    
    def write(self, data):
        self.buffer.append(data)
    
    def dispatch(self):
        plugin.dispatch(self.request, self)
        self.render()   
    
    def render(self):
        status = "HTTP/1.x 200 OK\r\n"
        self.headers['Content-length'] = str(sum([len(s) for s in self.buffer]))
        h = "\r\n".join(": ".join((k, v)) for (k, v) in self.headers.items())
        h += "\r\n\r\n"
        response = status + h + "".join(self.buffer)
        self.request.respond(HTTPContent(response))
        self.request.respond(HTTPRequestComplete())
    
