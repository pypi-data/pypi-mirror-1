from zope.interface import Interface
from zope.interface import implements
from zope.location.interfaces import ILocation

class IMyModel(Interface):
    pass

class MyModel(object):
    implements(IMyModel, ILocation)

    __name__ = None
    __parent__ = None

    def __getitem__(self, name):
        return MyModel()

    def absolute_path(self):
        p = []
        node = self
        while node.__name__ is not None:
            p.append(node.__name__)
            node = node.__parent__
        p.reverse()
        return "/".join(p)

root = MyModel()

def get_root(environ):
    return root
