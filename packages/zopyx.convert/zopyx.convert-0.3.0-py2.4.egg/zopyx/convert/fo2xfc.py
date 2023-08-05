##########################################################################
# zopyx.convert - XSL-FO related functionalities
#
# (C) 2007, ZOPYX Ltd & Co. KG, Tuebingen, Germany
##########################################################################

import os
import sys

from config import java
from util import newTempfile, runcmd
from logger import LOG

xfc_dir = os.environ.get('XFC_DIR')


def _check_xfc():
    if not xfc_dir:
        LOG.error('$XFC_DIR not set')
        return False

    if not os.path.exists(xfc_dir):
        LOG.error('$XFC=%s does not exist' % xfc_dir)
        return False

    return True

xfc_available = _check_xfc()

def fo2xfc(fo_filename, format='rtf', output_filename=None):
    """ Convert a FO file to some format support 
        through XFC-4.0.
    """

    if not format in ('rtf', 'docx', 'wml', 'odt'):
        raise ValueError('Unsupported format: %s' % format)

    if not output_filename:
        output_filename = newTempfile(suffix='.%s' % format)
    cmd = '"%s/fo2%s" "%s" "%s"' % (xfc_dir, format, fo_filename, output_filename)

    status, output = runcmd(cmd)
    if status != 0:
        raise RuntimeError('Error executing: %s' % cmd)

    return output_filename


def fo2rtf(fo_filename):
    return fo2xfc(fo_filename, 'rtf')

def fo2odt(fo_filename):
    return fo2xfc(fo_filename, 'odt')

def fo2docx(fo_filename):
    return fo2xfc(fo_filename, 'docx')

def fo2wml(fo_filename):
    return fo2xfc(fo_filename, 'wml')


def main():
    return fo2xfc(sys.argv[1], 'rtf')

if __name__ == '__main__':
    main()
