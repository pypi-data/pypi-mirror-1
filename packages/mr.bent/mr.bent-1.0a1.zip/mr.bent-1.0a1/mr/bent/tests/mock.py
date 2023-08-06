

def foo():
    return 42


def bar():
    return 42


def summary():
    foo()
    bar()


def reindex():
    return foo()


def fibbonaci(n):
    if n == 1:
        return 1
    elif n == 0:
        return 0
    else:
        return fibbonaci(n-1) + fibbonaci(n-2)


class page(object):

    def __init__(self, managers):
        self.managers = managers

    def render(self):
        output = ''
        for managers in self.managers:
            output += managers.render()
        foo()
        return output


class viewletmanager(object):

    def __init__(self, viewlets):
        self.viewlets = viewlets

    def render(self):
        output = ''
        reindex()
        for viewlet in self.viewlets:
            output += viewlet.render()
            bar()
        return output


class viewlet(object):

    def __init__(self, txt):
        self.txt = txt

    def render(self):
        summary()
        return self.txt + ' '

