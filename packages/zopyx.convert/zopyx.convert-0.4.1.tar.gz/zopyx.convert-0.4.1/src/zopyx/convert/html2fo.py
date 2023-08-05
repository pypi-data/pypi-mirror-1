##########################################################################
# zopyx.convert - XSL-FO related functionalities
#
# (C) 2007, ZOPYX Ltd & Co. KG, Tuebingen, Germany
##########################################################################

import os
import re
import mx.Tidy

from config import java
from util import newTempfile, runcmd

from zope.interface import implements
from interfaces import IHTML2FOConverter

dirname = os.path.dirname(__file__)


def tidyhtml(filename, encoding):

    # Tidy does not like uppercase names or names containg '-'
    encoding = encoding.lower().replace('-', '')

    html = open(filename, 'rb').read()
    nerrors, nwarnings, html, errordata = mx.Tidy.tidy(html,
                                                       drop_empty_paras=0,
                                                       char_encoding=encoding,
                                                       add_xml_decl=1,
                                                       output_xhtml=1)
    filename = newTempfile()
    open(filename, 'wb').write(html)
    return filename


class HTML2FOConverter(object):  

    implements(IHTML2FOConverter)

    def convert(self, filename, encoding='utf-8', language='en', country='en', tidy=True):
        """ Convert a HTML file stored as 'filename' to
            FO using CSS2XSLFO.
        """

        if tidy:
            filename = tidyhtml(filename, encoding)

        fo_filename = newTempfile(suffix='.fo')
        csstoxslfo = os.path.abspath(os.path.join(dirname, 'lib', 'csstoxslfo', 'css2xslfo.jar'))
        if not os.path.exists(csstoxslfo):
            raise IOError('%s does not exist' % csstoxslfo)

        cmd = '"%s"' % java + \
              ' -Xms128m -Xmx128m -jar "%(csstoxslfo)s" "%(filename)s" -fo "%(fo_filename)s" country=%(country)s language=%(language)s' % vars()

        status, output = runcmd(cmd)
        if status != 0:
            raise RuntimeError('Error executing: %s' % cmd)

        # remove tidy-ed file
        os.unlink(filename)

        # remove some stuff from the generated FO file causing
        # some conversion trouble either with XINC or XFC
        fo_text = open(fo_filename, 'rb').read()

        reg_s = '(footnote="reset")|'\
                '(unicode-bidi="embed")|'\
                '(writing-mode="lr-tb")|'\
                '(page-break-after="avoid")|'\
                '(page-break-before="avoid")|'\
                '(page-break-inside="avoid")'\

        reg = re.compile(reg_s, re.I|re.S|re.M)
        fo_text = reg.sub('', fo_text)

        fo_text = fo_text.replace('<fo:block ' , '<fo:block margin-top="0" margin-bottom="0" ')  # avoid a linebreak through <li><p> (XFC)
        fo_text = fo_text.replace('<fo:block/>', '') # causes a crash with XINC    

        # replace margin|padding-left|right|top-bottom="0" with ..="0em"
        def replacer(mo):
            return '%s-%s="0em"' % (mo.group(1), mo.group(2))

        reg = re.compile('(margin|padding)-(left|right|top|bottom)="0"', re.I|re.S|re.M)
        fo_text = reg.sub(replacer, fo_text)

        open(fo_filename, 'wb').write(fo_text)
        return fo_filename

