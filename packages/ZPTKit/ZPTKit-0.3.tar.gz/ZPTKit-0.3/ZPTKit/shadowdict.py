try:
    from UserDict import DictMixin
except ImportError:
    # DictMixin was added to Python 2.3
    from backports.UserDict import DictMixin

class ShadowDict(DictMixin):

    def __init__(self, component, attr):
        self.__dict__['_ShadowDict__component'] = component
        self.__dict__['_ShadowDict__attr'] = attr

    def __dict(self):
        return getattr(self.__component, self.__attr)

    def __getitem__(self, key):
        return self.__dict()[key]

    def __setitem__(self, key, value):
        self.__dict()[key] = value

    def __delitem__(self, key):
        del self.__dict()[key]

    def keys(self):
        return self.__dict().keys()

    def __contains__(self, key):
        return key in self.__dict()

    def __iter__(self):
        return iter(self.__dict())

    def iteritems(self):
        return self.__dict().iteritems()

    def __getattr__(self, key):
        if key.startswith('_'):
            raise AttributeError
        return self[key]

    def __setattr__(self, key, value):
        if key.startswith('_'):
            raise AttributeError
        self[key] = value
