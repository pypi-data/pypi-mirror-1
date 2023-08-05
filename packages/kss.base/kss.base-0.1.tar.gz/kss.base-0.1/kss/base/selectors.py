class Selector(object):
    def __init__(self, type, value):
        self.type = type
        self.value = value

    def __str__(self):
        return "%s('%s')" % (self.type, self.value)
