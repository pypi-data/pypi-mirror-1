from sys import modules


def funcinfo(function):
    """ returns the container (class or module) and name of a function """
    while hasattr(function, '__original__'):    # let's find the...
        function = function.__original__        # original container
    if hasattr(function, 'im_class'):
        container = function.im_class
    else:
        container = modules[function.__module__]
    return container, function.__name__


def wrap(function, handler):
    """ monkey-patch a function using the given wrapper generator """
    container, name = funcinfo(function)
    def wrapper(*args, **kw):
        return handler(function, *args, **kw)
    wrapper.__doc__ = function.__doc__
    wrapper.__original__ = function
    setattr(container, name, wrapper)


def unwrap(function):
    """ unwrap a previously wrapped function """
    if hasattr(function, '__original__'):
        container, name = funcinfo(function.__original__)
        setattr(container, name, function.__original__)

