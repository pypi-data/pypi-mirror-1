class Registry(object):
    def __init__(self):
        self._items = {}

    def register(self, name, factory):
        if name in self._items:
            raise KeyError('Duplicate registration for name: %s' % name)
        self._items[name] = factory

    def unregister(self, name):
        del self._items[name]

    def get(self, name):
        return self._items[name]

    def items(self):
        return self._items.iteritems()

command_set_registry = Registry()
plugin_registry = Registry()
