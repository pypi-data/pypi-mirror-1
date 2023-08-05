import os

from kss.base.plugin import activated_plugins
from kss.base.compression.javascript import compress

def concatinated(include_extras=False):
    '''Concatinate the Javascript files for all activate plugins'''
    scripts = []
    
    for id, plugin in sorted(activated_plugins(), 
                             key=lambda item: item[1].priority):
        if include_extras:
            javascripts = plugin.javascripts + plugin.extra_javascripts
        else:
            javascripts = plugin.javascripts
        for filename in javascripts:
            f = open(filename, 'r')
            scripts.append(f.read())
            f.close()

    return '\n'.join(scripts)

def packed(compression_level=None, include_extras=False):
    return compress(concatinated(include_extras), compression_level)

def extra_scripts():
    '''Return a dictionary of the extra javascripts for all activated
       plugins'''

    scripts = {}
    for id, plugin in activated_plugins():
        for filename in plugin.extra_javascripts:
            f = open(filename, 'r')
            scripts[os.path.basename(filename)] = f.read()
            f.close()
    return scripts
    
 
