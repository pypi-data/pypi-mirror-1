from mavolio import create, destroy, current, add, filters
from monkey import funcinfo, wrap


def fqfn(function):
    """ return the fully qualified name for the given function """
    if hasattr(function, 'im_class'):
        container, name = funcinfo(function)
        components = container.__module__, container.__name__, name
    else:
        components = function.__module__, function.__name__
    return '.'.join(components)


def mkcontext(function, callback):
    """ wrap the given function to create a stats context for it """
    name = fqfn(function)
    def wrapper(function, *args, **kw):
        create(name)
        result = function(*args, **kw)
        stats = destroy()
        obj = args and args[0] or None
        return callback(obj, result, stats)
    wrap(function, wrapper)


def mkwrapper(function, handler, name):
    """ wrap a function using a given handler function, returning the correct
        value and adding the gathered data to the current context """
    dottedname = fqfn(function)
    def wrapper(function, *args, **kwargs):
        context = current()
        if context is not None:
            data, result = handler(function, *args, **kwargs)
            add(context, (None, dottedname, name), data)
            for f in filters:
                add(context, (f, dottedname, name), data)
            return result
        else:
            return function(*args, **kwargs)    # shortcut without handler
    wrap(function, wrapper)


def mkfilter(function, name=None):
    """ wrap a function in order to define a filter;  a filter will give
        additional results for watched function limited to the duration
        of the function it was applied to """
    if name is None:
        name = fqfn(function)
    def wrapper(function, *args, **kwargs):
        filters.add(name)
        results = function(*args, **kwargs)
        filters.remove(name)
        return results
    wrap(function, wrapper)

