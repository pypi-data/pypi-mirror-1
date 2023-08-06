def path_to_object(path):
    """Returns a Python object from a string path"""
    dot = '.' in path and path.rindex('.') or None
    
    if dot:
        f_mod, f_obj = path[:dot], path[dot+1:]

        mod = __import__(f_mod, {}, {}, [''])
        obj = getattr(mod, f_obj)
    else:
        obj = __import__(path, {}, {}, [''])

    return obj

def split1000(s, sep=','):
    """http://www.python.org.br/wiki/FormatarNumeros"""
    #return s if len(s) <= 3 else split1000(s[:-3], sep) + sep + s[-3:]
    return len(s) <= 3 and s or split1000(s[:-3], sep) + sep + s[-3:]

