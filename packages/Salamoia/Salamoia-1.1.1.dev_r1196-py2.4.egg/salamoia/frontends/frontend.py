import os,string
from config import Config

from salamoia.h2o.decorators.lazy import *

installedFrontends = {}
server="n"

__optionProcessingDone = False

def prepareOptionProcessing(cls):
    global __optionProcessingDone
    if __optionProcessingDone:
        return

    if not cls.optionParser:
        from optparse import OptionParser
        cls.optionParser  = OptionParser()

    optionParser = cls.optionParser
    optionParser.add_option('-c', '--configfile',
                            action='store', type='string', dest='config',
                            default=None,
                            help='read configuration from this file')
    optionParser.add_option('-F', '--frontends',
                            action='store', type='string', dest='frontends',
                            help='set preferred frontends list')
    optionParser.add_option('-p', '--profile',
                            action='store', type='string', dest='profile',
                            help='set connection parameters profile')
    optionParser.add_option('-e', '--embedded',
                            action='store_true', dest='embedded',
                            default=False,
                            help='use embedded nacl')
    for i in installedFrontends.values():
        group = i.options(optionParser)
        if group:
            optionParser.add_option_group(group)

    __optionProcessingDone = True

class Frontend:
    
    optionParser = None

    def __init__(self):
        None
    
    def defaultFrontend(cls):
        prepareOptionProcessing(cls)
        frontend_names = installedFrontends.keys()
        default = 'qt ncurses ashella cli oliva sansa'

        # opt
        options, args = cls.optionParser.parse_args()
        conf = options.frontends

        if options.profile:
            from client import Client
            Client.setDefaultProfile(options.profile)

        if options.config:
            Config.setConfigFile(options.config)

        # env
        if not conf:
            conf = os.getenv('SALAMOIA_FRONTENDS')
        # conf
        if not conf:
            cfg = Config()
            conf = cfg.get('General', 'Frontends', default)

        # match
        preferred_names = conf.split()
        for i in preferred_names:
            if i in frontend_names:
                if installedFrontends[i].checkEnv():
                    return installedFrontends[i]

        return None

    defaultFrontend = classmethod(defaultFrontend)
        
    def addFrontend(cls, frontend):
        installedFrontends[frontend.name()] = frontend
        
    addFrontend = classmethod(addFrontend)

    def checkEnv(self):
        if self.requiresGui() and not os.getenv('DISPLAY'):
            return False
        return True

    def requiresGui(self):
        return False

    def requiresTty(self):
        return False

    def options(self, parser):
        return None

    def run(self):
        print "error: sublcass shoud implement run method"

# import frontends

# try:
#     import frontends.qt.frontend
# except:
#     pass

# try:
#     import frontends.ncurses.frontend
# except:
#     pass

# try:
#     import frontends.cli.frontend
# except:
#     raise

# try:
#     import frontends.ashella.frontend
# except:
#     raise

from salamoia.h2o.logioni import Ione
try:
    import salamoia.frontends.oliva
    import salamoia.frontends.oliva.frontend
    Frontend.addFrontend(salamoia.frontends.oliva.frontend.OlivaFrontend())
except:
    raise

#try:
#    import salamoia.frontends.http.frontend
#    Frontend.addFrontend(salamoia.frontends.http.frontend.HTTPFrontend())
#except:
#    raise

#try:
#    import frontends.sansa.frontend
#except:
#    raise
