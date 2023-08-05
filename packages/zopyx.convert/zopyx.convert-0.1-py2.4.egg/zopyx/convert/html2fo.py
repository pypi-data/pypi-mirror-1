##########################################################################
# zopyx.convert - XSL-FO related functionalities
#
# (C) 2007, ZOPYX Ltd & Co. KG, Tuebingen, Germany
##########################################################################

import os
import sys

from config import java
from util import newTempfile, runcmd

dirname = os.path.dirname(__file__)


def html2fo(filename, language='en', country='en'):
    """ Convert a HTML file stored as 'filename' to
        FO using CSS2XSLFO.
    """

    fo_filename = newTempfile(suffix='.fo')
    csstoxslfo = os.path.abspath(os.path.join(dirname, 'lib', 'csstoxslfo', 'css2xslfo.jar'))
    if not os.path.exists(csstoxslfo):
        raise IOError('%s does not exist' % csstoxslfo)

    cmd = '"%s"' % java + \
          ' -Xms128m -Xmx128m -jar "%(csstoxslfo)s" "%(filename)s" -fo "%(fo_filename)s" country=%(country)s language=%(language)s' % vars()

    status, output = runcmd(cmd)
    if status != 0:
        raise RuntimeError('Error executing: %s' % cmd)

    return fo_filename


def main():
    sys.exit(html2fo(sys.argv[1]))

if __name__ == '__main__':
    main()
