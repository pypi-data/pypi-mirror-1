import optparse
import ConfigParser

from paste.script.templates import Template

from kss.base.javascript import packed
from kss.base.plugin import load_plugins, activated_plugins


class KSSConcatJs(object):
    '''Prints out or saves a packed javascript of loaded plugins'''

    configSection = "KSSConcatJs"

    def __init__(self):
        self.getOptions()
        if self.options.configFile:
            self.getConfig(self.options.configFile)
        self.handleCreation()


    def getOptions(self):
        '''Gets the arguments passed to the script (override config)'''
        parser = optparse.OptionParser()

        parser.add_option('-m', '--message',
            action='store',
            dest='message',
            help="message (comment) that will be added to the generated javascript")
        parser.add_option('--list',
            action='store_true',
            dest='listPlugins',
            help="lists activated plugins")
        parser.add_option('--compression-level',
            action='store',
            dest='compressionLevel',
            help="specifies the compression level (devel / stripped / safe / full / safe-devel / full-devel)")
        parser.add_option('--plugin',
            action='append',
            dest='pluginsToHandle',
            help="specifies one additional plugin to load; if you want to specify multiple plugins you can do it by calling --plugin multiple times")
        parser.add_option('--no-display',
            action='store_true',
            dest='noDisplayJavascript',
            help="avoids the display of resulting javascript in console")
        parser.add_option('--output-file',
            action='store',
            dest='outputFile',
            help="outputs the resulting javascript to the specified file")
        parser.add_option('--include-extras',
            action='store',
            dest='includeExtras',
            help="specifies if 3rd party javascripts have to be packed too")
        parser.add_option('-v', '--verbose',
            action='store_true',
            dest='verboseMode',
            help="verbose mode")
        parser.add_option('-F',
            action='store',
            dest='configFile',
            help="loads options from the specified config file")

        options, args = parser.parse_args()
        self.options = options


    def getConfig(self, fileName):
        '''Gets the values in config file only if not overrided by argument'''
        config = ConfigParser.ConfigParser()
        config.read(fileName)
        listParameters = ['pluginsToHandle']
        strParameters = ['compressionLevel', \
                         'outputFile']
        boolParameters = ['listPlugins', \
                          'noDisplayJavascript', \
                          'includeExtras', \
                          'verboseMode']
        for param in strParameters:
            if not hasattr(self.options, param):
                try:
                    setattr(self.options, \
                            param, \
                            config.get(self.configSection, param))
                except ConfigParser.NoOptionError:
                    pass
        for param in boolParameters:
            if not hasattr(self.options, param):
                try:
                    setattr(self.options, \
                            param, \
                            config.getboolean(self.configSection, param))
                except ConfigParser.NoOptionError:
                    pass
        for param in listParameters:
            #this is a list so the condition doesn't work with hasattr
            if not bool(self.options.pluginsToHandle):
                try:
                    paramList = config.get(self.configSection, param).split(' ')
                    setattr(self.options, \
                            param, \
                            paramList)
                except ConfigParser.NoOptionError:
                    pass


    def makeJS(self, compressionLevel=None, includeExtras=False):
        '''Returns a compacted javascript generated from loaded javascripts'''
        return packed(compressionLevel, include_extras=False)


    def setComment(self, javascript, message):
        '''Add a comment to the generated javascript'''
        return "/* %s */\n\n%s" % (message, javascript)

    def writeToFile(self, fileName, fileContent):
        '''Writes the packed javascript to file'''
        file = open(fileName, 'w')
        file.write(fileContent)
        file.close()


    def listPlugins(self):
        '''Displays activated plugins'''
        if self.options.verboseMode:
            print "Activated plugins :"
            for id, plugin in activated_plugins():
                print " * %s" % id
        else:
            for id, plugin in activated_plugins():
                print id


    def handleCreation(self):
        '''Handles the JS creation regarding options and/or config'''
        corePlugin = ('kss-core', )
        if self.options.pluginsToHandle:
            plugins = tuple(self.options.pluginsToHandle) + corePlugin
        else:
            plugins = corePlugin
        self.loadedPlugins = load_plugins(*plugins)

        if self.options.listPlugins:
            self.listPlugins()

        javascript = self.makeJS(self.options.compressionLevel, \
                                 self.options.includeExtras)

        if self.options.message:
            javascript = self.setComment(javascript, self.options.message)

        if self.options.outputFile:
            self.writeToFile(self.options.outputFile, javascript)
        elif not self.options.noDisplayJavascript:
            print javascript


class KSSPluginTemplate(Template):
    _template_dir = 'templates/plugin'
    summary = 'KSS plugin template'
    egg_plugins = ['kss.base']
