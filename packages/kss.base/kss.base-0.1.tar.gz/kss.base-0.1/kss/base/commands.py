from xml.sax.saxutils import quoteattr, escape
from kss.base.registry import command_set_registry
from kss.base.selectors import Selector
from kss.base.coreselectors import css

kss_response_header = '''<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:kukit="http://www.kukit.org/commands/1.0"><body><kukit:commands>'''

kss_response_footer = '</kukit:commands></body></html>'

kss_command_start = '<kukit:command selector=%(selector)s name=%(action)s selectorType=%(selector_type)s>'

kss_command_end = '</kukit:command>'

kss_param = '<kukit:param name=%(name)s>%(value)s</kukit:param>'

class KSSCommands(object):
    '''Command renderer for creating KSS responses'''
    def __init__(self):
        self.commands = []

    def add(self, action, selector, **kwargs):
        self._strip_none_parameters(kwargs)

        if selector is not None and not isinstance(selector, Selector):
            selector = css(selector)

        self.commands.append((action, selector, kwargs))

    def _strip_none_parameters(self, parameters):
        for key, value in parameters.items():
            if value is None:
                del parameters[key]

    def render(self):
        output = [kss_response_header]
        for action, selector, options in self.commands:
            output.append(kss_command_start % dict(
                selector=quoteattr(selector.value),
                selector_type=quoteattr(selector.type),
                action=quoteattr(action)))
            for name, value in options.items():
                output.append(kss_param % dict(
                    name=quoteattr(name), value=escape(value)))
            output.append(kss_command_end)
        output.append(kss_response_footer)
        return ''.join(output)

    def clear(self):
        self.commands = []

    def __str__(self):
        def format_options(options):
            if not options:
                return ''
            return ', ' + ', '.join(
                ["%s='%s'" % item for item in options.items()])

        lines = []
        for action, selector, options in self.commands:
            lines.append("%(action)s(%(selector)s%(options)s)" % {
                    'action': action,
                    'selector': selector,
                    'options': format_options(options)})
        return '\n'.join(lines)

    def __getattr__(self, name):
        return command_set_registry.get(name)(self)

class KSSCommandSet(object):
    def __init__(self, commands):
        self.commands = commands
