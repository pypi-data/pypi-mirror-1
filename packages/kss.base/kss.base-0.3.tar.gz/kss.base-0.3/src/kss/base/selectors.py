from kss.base.registry import Registry

class Selector(object):
    """A base for selectors. Plugins that implement this, need
    to implement __init__ themselves, and set type as a string.

    Currently only the 'type' and 'value' attribute gets marshalled,
    but this may change in later implementations.
    """
    type = None
    value = ''

    def __init__(self):
        raise NotImplementedError

    def __str__(self):
        return "%s('%s')" % (self.type, self.value)


class css(Selector):
    type = 'css'

    def __init__(self, value):
        self.value = value

class htmlid(Selector):
    type = 'htmlid'

    def __init__(self, value):
        self.value = value

class samenode(Selector):
    type = 'samenode'

    def __init__(self):
        pass

class parentnode(Selector):
    type = 'parentnode'

    def __init__(self, value):
        self.value = value

selectors = Registry()
