from smtplib import *
from salamoia.h2o.logioni import *

def sendmail(mail):
    # da perendere in nacl.conf
    server   =  SMTP('localhost')
    server.set_debuglevel(1)
    try:
        dest = mail['To']
        cc = mail["Cc"]
        if type(dest) == type(""):
            dest = [dest]
        if type(cc) == type(""):
            cc = [cc]
        if cc:
            dest = dest + cc
        Ione.log("SENDING TO %s" % (dest))
        server.sendmail(mail['From'], dest, mail.as_string())
    except:
        Ione.log("Mail form:%s to:%s" % (mail['From'],mail['To']))
        server.quit()
        return 0

    server.quit()
    return 1

# -- run the doc tests in this document if invoked as a script
from salamoia.tests import *; runDocTests()
# --
