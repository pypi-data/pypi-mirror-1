from salamoia.frontends.frontend import *
from optparse import OptionGroup
#from salamoia.frontends.client import *

import xmlrpclib
import code

import readline
import atexit
import os

from salamoia.h2o.xmlclient import Client
from salamoia.frontends.config import Config

class Console(Frontend):
    def name(self):
        return "console"

    def options(self, parser):
        "Return an option group specifing the front end specific options"
        
        from optparse import OptionGroup
        optionGroup = OptionGroup(parser,
                                 "Salamoia console options")
        optionGroup.add_option('-b', '--base',
                               type='string', dest='base',
                               help='base url')
        optionGroup.add_option('-p', '--port',
                               type='string', dest='port',
                               help='port')
        optionGroup.add_option('-H', '--host',
                               type='string', dest='host',
                               help='host')
        #optionGroup.add_option('-u', '--url',
        #                       type='string', dest='url',
        #                       help='url (overrides host port and base)')
        return optionGroup

    
    def run(self):
        options, args = self.optionParser.parse_args()
        self.options = options
        self.args = args
        
        historyPath = os.path.expanduser("~/.salamoia-console-history")

        def save_history(historyPath=historyPath):
            import readline
            readline.write_history_file(historyPath)

        if os.path.exists(historyPath):
            readline.read_history_file(historyPath)

        atexit.register(save_history)


        cfg = Config.defaultConfig()
        username = cfg.get('general', 'username')
        password = cfg.get('general', 'password')
        
        port = cfg.get('general', 'port')
        if self.options.port:
            port = self.options.port

        host = "localhost"
        if self.options.host:
            host = self.options.host
        
        base = "hostello"
        if self.options.base:
            base = self.options.base
        # se ticket #50
        #base = ""        

        server = Client(host, port, base=base, username=username, password=password)

        code.interact(local={'server': server, 's': server, '__server__': server},
                      banner="Salamoia python interactive console")


def start():
    Console.start()

