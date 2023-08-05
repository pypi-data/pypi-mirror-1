from kss.base.commands import KSSCommandSet

class KSSCoreCommands(KSSCommandSet):

    def setAttribute(self, selector, name, value):
        self.commands.add('setAttribute', selector, name=name, value=value)

    def setStyle(self, selector, name, value):
        if ' ' in name:
            raise ValueError('Style properites cannot contain spaces')
        self.commands.add('setStyle', selector, name=name, value=value)

    def addClass(self, selector, value):
        self.commands.add('addClass', selector, value=value)

    def removeClass(self, selector, value):
        self.commands.add('removeClass', selector, value=value)

    def toggleClass(self, selector, value):
        self.commands.add('toggleClass', selector, value=value)

    def focus(self, selector):
        self.commands.add('focus', selector)

    def replaceInnerHTML(self, selector, value, withKssSetup=True):
        """Replace the contents of a node (selector) with the new `value`"""
        extra_args = {}
        if not withKssSetup:
            extra_args['withKssSetup'] = 'False'
        self.commands.add('replaceInnerHTML', selector, html=value, 
                          **extra_args)

    def replaceHTML(self, selector, value, withKssSetup=True):
        extra_args = {}
        if not withKssSetup:
            extra_args['withKssSetup'] = 'False'
        self.commands.add('replaceHTML', selector, html=value,
                          **extra_args)

    def insertHTMLBefore(self, selector, value):
        self.commands.add('insertHTMLBefore', selector, html=value)

    def insertHTMLAfter(self, selector, value):
        self.commands.add('insertHTMLAfter', selector, html=value)

    def insertHTMLAsFirstChild(self, selector, value):
        self.commands.add('insertHTMLAsFirstChild', selector, html=value)

    def insertHTMLAsLastChild(self, selector, value):
        self.commands.add('insertHTMLAsLastChild', selector, html=value)



    def deleteNode(self, selector):
        self.commands.add('deleteNode', selector)

    def deleteNodeBefore(self, selector):
        self.commands.add('deleteNodeBefore', selector)

    def deleteNodeAfter(self, selector):
        self.commands.add('deleteNodeAfter', selector)

    def clearChildNodes(self, selector):
        self.commands.add('clearChildNodes', selector)
    
    

    def copyChildNodesFrom(self, selector, id):
        self.commands.add('copyChildNodesFrom', selector, html_id=id)

    def copyChildNodesTo(self, selector, id):
        self.commands.add('copyChildNodesTo', selector, html_id=id)



    def moveNodeBefore(self, selector, id):
        self.commands.add('moveNodeBefore', selector, html_id=id)

    def moveNodeAfter(self, selector, id):
        self.commands.add('moveNodeAfter', selector, html_id=id)


    def setStateVar(self, varname, value):
        self.commands.add('setStateVar', None, varname=varname, value=value)

    def triggerEvent(self, name, **kwargs):
        self.commands.add('triggerEvent', None, name=name, **kwargs)



