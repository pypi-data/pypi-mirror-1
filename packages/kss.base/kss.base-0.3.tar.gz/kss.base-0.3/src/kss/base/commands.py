from xml.sax.saxutils import quoteattr, escape
from kss.base.registry import command_set_registry
from kss.base.selectors import Selector

kss_response_header = '''<?xml version="1.0" ?>
<kukit xmlns="http://www.kukit.org/commands/1.1"><commands>
'''

kss_response_footer = '</commands></kukit>'

kss_command_start = '<command selector=%(selector)s name=%(action)s selectorType=%(selector_type)s>'

kss_command_start_global = '<command name=%(action)s>'

kss_command_end = '</command>'

kss_param = '<param name=%(name)s>%(value)s</param>'

class cdatadata(object):
    def __init__(self, value):
        self.value = value

    def node(self):
        '''Return the XML node representation of this object'''
        return '<![CDATA[%s]]>' % self.value.replace(']]>', ']]&gt;')

    def __repr__(self):
        return "%s('%s')" % (self.__class__.__name__, self.value)

class htmldata(cdatadata):
    pass

class xmldata(cdatadata):
    pass

class KSSCommands(object):
    '''Command renderer for creating KSS responses'''
    def __init__(self):
        self.commands = []

    def add(self, action, selector, **kwargs):
        self._strip_none_parameters(kwargs)

        self.commands.append((action, selector, kwargs))

    def _strip_none_parameters(self, parameters):
        for key, value in parameters.items():
            if value is None:
                del parameters[key]

    def render(self):
        output = [kss_response_header]
        for action, selector, options in self.commands:
            if selector is None:
                output.append(kss_command_start_global % dict(
                        action=quoteattr(action)))
            else:
                try:
                    selector_type = selector.type
                    selector = selector.value
                except AttributeError:
                    # It is probably a string or unicode object so we
                    # can let the client decide the default selector
                    selector_type = ''

                output.append(kss_command_start % dict(
                        selector=quoteattr(selector),
                        selector_type=quoteattr(selector_type),
                        action=quoteattr(action)))
                
            for name, value in options.items():
                try:
                    node = value.node()
                except AttributeError:
                    # If it the value does not explicitly convert to a
                    # node make it a text node, unless it is larger
                    # than 4KB (since this triggers a problem with
                    # Firefox and large text nodes).
                    if len(value)>= 4096:
                        node = cdatadata(value).node()
                    else:
                        node = escape(value)
                output.append(kss_param % dict(
                    name=quoteattr(name), value=node))
            output.append(kss_command_end)
        output.append(kss_response_footer)
        return ''.join(output)

    def clear(self):
        self.commands = []

    def __str__(self):
        lines = []
        for action, selector, options in self.commands:
            line = '%s(' % action
            if isinstance(selector, Selector):
                line += '%s' % selector
            elif isinstance(selector, basestring):
                line += "'%s'" % selector
            
            if options:
                if selector is not None:
                    line += ', '
                line += ', '.join(
                    ["%s=%r" % (key, value) for 
                     key, value in options.items()])
            lines.append(line + ')')
        return '\n'.join(lines)

    def __getattr__(self, name):
        return command_set_registry.get(name)(self)

class KSSCommandSet(object):
    def __init__(self, commands):
        self.commands = commands
