##########################################################################
# zopyx.convert - XSL-FO related functionalities
#
# (C) 2007, ZOPYX Ltd & Co. KG, Tuebingen, Germany
##########################################################################

import os
import sys

from config import java
from util import newTempfile, runcmd

xfc_dir = os.environ.get('XFC_DIR')
if not xfc_dir:
    raise ValueError('$XFC_DIR not set')

if not os.path.exists(xfc_dir):
    raise IOError('$XFC=%s does not exist' % xfc_dir)


def fo2xfc(fo_filename, format='rtf'):
    """ Convert a FO file to some format support 
        through XFC-4.0.
    """

    if not format in ('rtf', 'docx', 'wml', 'odt'):
        raise ValueError('Unsupported format: %s' % format)

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
