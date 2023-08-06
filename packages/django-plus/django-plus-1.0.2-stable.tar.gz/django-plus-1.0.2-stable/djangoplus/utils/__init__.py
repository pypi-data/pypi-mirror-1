def path_to_object(path):
    dot = '.' in path and path.rindex('.') or None
    
    if dot:
        f_mod, f_obj = path[:dot], path[dot+1:]

        mod = __import__(f_mod, {}, {}, [''])
        obj = getattr(mod, f_obj)
    else:
        obj = __import__(path, {}, {}, [''])

    return obj

