##########################################################################
# zopyx.convert - XSL-FO related functionalities
#
# (C) 2007, ZOPYX Ltd & Co. KG, Tuebingen, Germany
##########################################################################

import os
import sys

from config import java
from util import newTempfile, runcmd

xinc_home = os.environ.get('XINC_HOME')
if not xinc_home:
    raise ValueError('$XINC_HOME not set')

if not os.path.exists(xinc_home):
    raise IOError('$XINC_HOME=%s does not exist' % xinc_home)


def fo2pdf(fo_filename):
    """ Convert a FO file to PDF using XINC """


    output_filename = newTempfile(suffix='.pdf')
    cmd = '"%s/bin/unix/xinc" -fo "%s" -pdf "%s"' % (xinc_home, fo_filename, output_filename)

    status, output = runcmd(cmd)
    if status != 0:
        raise RuntimeError('Error executing: %s' % cmd)

    return output_filename

