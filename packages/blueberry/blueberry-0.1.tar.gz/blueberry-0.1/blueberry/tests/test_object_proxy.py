from blueberry.utils import ObjectProxy

# Object proxies are used for accessing thread-local global objects.
# Pylons uses a stack for each thread-local object

def test1():
    proxy = ObjectProxy('proxy')
    proxy.set(dict(foo='hello world'))
    assert 'foo' in proxy.keys()
    assert 'ObjectProxy' == proxy.__class__.__name__

class Foo(object):

    def __init__(self, name):
        self.name = name

def test2():
    foo = ObjectProxy('foo')
    foo.set(Foo('david'))
    assert 'david' == foo.name
    assert 'ObjectProxy' == foo.__class__.__name__
