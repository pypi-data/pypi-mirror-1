class JsonHolder(object):
    pass
json = JsonHolder()
try:
    import cjson
    json.encode = cjson.encode
    json.decode = cjson.decode
except ImportError:
    try:
        import simplejson
        json.encode = simplejson.dumps
        json.decode = simplejson.loads
    except ImportError:
        try:
            import demjson
            json.encode = demjson.encode
            json.decode = demjson.decode
        except ImportError:
            raise ImportError, "Orbited 0.3.x requires either demjson, simplejson, or cjson"
        
        