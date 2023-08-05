import os

from kss.base.plugin import Plugin
from kss.base.corecommands import KSSCoreCommands
from kss.base.coreselectors import css, htmlid, samenode, parentnode

kukit_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'kukit')

# Define the Javascripts by hand to ensure the order
core_js = ['utils.js',
           'errors.js',
           'oper.js',
           'kukit.js',
           'tokenizer.js',
           'providerreg.js',
           'resourcedata.js',
           'kssparser.js',
           'eventreg.js',
           'actionreg.js',
           'dom.js',
           'commandreg.js',
           'serveraction.js',
           'requestmanager.js',
           'commandprocessor.js',
           'selectorreg.js',
           'forms.js',
           'plugin.js',
           ]

third_party_js = [
    'base2-dom-fp.js',
    'sarissa.js',
]

class KSSCore(Plugin):
    '''The KSS core plugin has all the standard functionality'''

    priority = -1000

    javascripts = [os.path.join(kukit_dir, 'kukit', js) for js in core_js]

    extra_javascripts = [os.path.join(kukit_dir, '3rd_party', f)
                         for f in third_party_js]
                                           
    commandsets = {
        'core': KSSCoreCommands,
        }

    selectors = [css, htmlid, samenode, parentnode]

