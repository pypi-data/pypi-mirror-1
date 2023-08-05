import os

from pkg_resources import iter_entry_points

from kss.base.registry import command_set_registry, plugin_registry
from kss.base import selectors as kss_selectors

class Plugin(object):
    priority = 100

    javascripts = ()
    extra_javascripts = ()
    selectors = ()
    commandsets = {}

    def register_commandsets(self, registry):
        for name, commandset in self.commandsets.iteritems():
            registry.register(name, commandset)

    def unregister_commandsets(self, registry):
        for name, commandset in self.commandsets.iteritems():
            registry.unregister(name)

    def register_selectors(self):
        for selector in self.selectors:
            setattr(kss_selectors, selector.__name__, selector)

    def unregister_selectors(self):
        for selector in self.selectors:
            delattr(kss_selectors, selector.__name__)


def javascripts_from(path):
    javascripts = []
    if not os.path.isdir(path):
        raise ValueError('Path is not a directory: %s' % path)

    for dirpath, dirnames, filenames in os.walk(path):
        for filename in filenames:
            if filename.endswith('.js'):
                javascripts.append(os.path.join(dirpath, filename))
    return javascripts
    
def module_path(mod):
    return os.path.join(os.path.dirname(os.path.abspath(mod.__file__)))

def file_below_module(mod, subpath):
    return os.path.join(module_path(mod), *subpath.split('/'))

def available_plugins():
    plugins = []

    for entry_point in iter_entry_points('kss.plugin'):
        plugin_factory = entry_point.load()
        plugin = plugin_factory()
        plugins.append((entry_point.name, plugin))

    return sorted(plugins, 
                  key=lambda item: item[1].priority)

def load_plugins(*names):
    def load(name):
        for entry_point in iter_entry_points('kss.plugin', name):
            plugin_factory = entry_point.load()

            plugin = plugin_factory()
            plugin_registry.register(name, plugin)
            # Setup of all hooks
            plugin.register_commandsets(command_set_registry)
            plugin.register_selectors()
            return
        raise KeyError("Plugin is not registered: %s" % name)

    for name in names:
        load(name)

def unload_plugins(*names):
    for name in names:
        for entry_point in iter_entry_points('kss.plugin', name):
            plugin_factory = entry_point.load()

            plugin = plugin_factory()
            # Tear down of all hooks
            plugin.unregister_commandsets(command_set_registry)
            plugin.unregister_selectors()

            plugin_registry.unregister(name)
    

def activated_plugins():
    return plugin_registry.items()

