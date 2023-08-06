from copy import copy

stack = []
filters = set()


def create(name):
    """ create a new context """
    stack.append(context(name))


def destroy():
    """ create a new context """
    top = stack.pop()
    parent = current()
    if parent is not None:
        parent.propagate(top)
    return top


def current():
    """ return the current context """
    if stack:
        return stack[-1]
    else:
        return None


def add(mapping, key, value):
    """ set or add to an existing value """
    if mapping.has_key(key):
        mapping[key] += value
    else:
        mapping[key] = copy(value)


class context(dict):
    """ a context/scope for collecting data """

    def __init__(self, name):
        self.name = name

    def propagate(self, values):
        for key, value in values.items():
            add(self, key, value)

