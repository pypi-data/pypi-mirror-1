

def convert(mapping):
    """ convert a mapping which contains tuples as its keys into a nested
        mapping with the tuples split up and used as keys in each of the
        dictionaries """
    nested = {}
    for key, value in mapping.items():
        local = nested
        if isinstance(key, tuple):
            key = list(key)
            while len(key) > 1:
                first = key.pop(0)
                local = local.setdefault(first, {})
            if len(key) == 1:
                key, = key      # unwrap the tuple
        local[key] = value
    name = getattr(mapping, 'name', None)
    if name is not None:
        nested['name'] = name
    return nested

