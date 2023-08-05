from kss.base.selectors import Selector

class css(Selector):
    def __init__(self, value):
        super(css, self).__init__('css', value)

class htmlid(Selector):
    def __init__(self, value):
        super(htmlid, self).__init__('htmlid', value)

class samenode(Selector):
    def __init__(self):
        super(samenode, self).__init__('samenode', '')

class parentnode(Selector):
    def __init__(self, value):
        super(parentnode, self).__init__('parentnode', value)
