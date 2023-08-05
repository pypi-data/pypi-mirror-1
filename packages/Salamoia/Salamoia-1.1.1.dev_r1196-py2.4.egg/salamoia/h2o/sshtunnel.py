import sys, os
from exception import *

class SSHTunnel(object):
    def __init__(self, hostname, localport, remoteport, remotehost='localhost'):
        self.cmd = "ssh %s -C -L %s:%s:%s 'echo ok; cat'" % (hostname, localport, remotehost, remoteport)        

    def run(self):
        self.pipe = os.popen3(self.cmd)

    def waitShell(self):
        str =  self.pipe[1].readline()
        if str != 'ok\n':
            raise ProtocolError, "expected ok from ssh"
        
