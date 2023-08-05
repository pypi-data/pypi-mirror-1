##########################################################################
# zopyx.convert - XSL-FO related functionalities
#
# (C) 2007, ZOPYX Ltd & Co. KG, Tuebingen, Germany
##########################################################################

import os
import sys
import tempfile
import commands

win32 = (sys.platform=='win32')

def newTempfile(suffix=None):
    return tempfile.mktemp(suffix=suffix)


def runcmd(cmd):                

    if win32:
        raise NotImplementedError('No windows support so far')

    else:      
        status, output = commands.getstatusoutput(cmd)
        return status, output
