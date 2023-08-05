##########################################################################
# zopyx.convert - XSL-FO related functionalities
#
# (C) 2007, ZOPYX Ltd & Co. KG, Tuebingen, Germany
##########################################################################

import os
import re

from config import java
from util import newTempfile, runcmd
from elementtree.ElementTree import parse, tostring        
from htmlentitydefs import name2codepoint
from BeautifulSoup import BeautifulSoup

from zope.interface import implements
from interfaces import IHTML2FOConverter

dirname = os.path.dirname(__file__)


def tidyhtml(filename, encoding):

    html = open(filename, 'rb').read()

    # use BeautifulSoup for performing HTML checks
    # and conversion to XHTML
    soup = BeautifulSoup(html)

    # check if all image files exist
    for img in soup.findAll('img'):
        src = img['src']
        if not os.path.exists(src):
            raise IOError('No image file found: %s' % src)

    html = str(soup.prettify())

    # replace the HTML tag
    html = '<html xmlns="http://www.w3.org/1999/xhtml">' + \
            html[html.find('<html') + 6:]
    # add the XML preamble
    html = '<?xml version="1.0" ?>\n' + html

    # replace all HTML entities with numeric entities
    def handler(mo):
        """ Callback to convert entities """
        e = mo.group(1)
        v = e[1:-1]
        if not v.startswith('#'):
            codepoint =  name2codepoint.get(v)
            return codepoint and '&#%d;' % codepoint or ''
        else:
            return e
    
    entity_reg = re.compile('(&.*?;)')
    html = entity_reg.sub(handler, html)

    filename = newTempfile()
    open(filename, 'wb').write(str(html))
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

        E = parse(fo_filename)

        for node in E.getiterator():

            get = node.attrib.get
            
            for k, v in (('footnote', 'reset'), 
                         ('unicode-bidi', 'embed'), 
                         ('writing-mode', 'lr-tb'), 
                         ('font-selection-strategy', 'character-by-character'), 
                         ('line-height-shift-adjustment', 'disregard-shifts'), 
                         ('page-break-after', 'avoid'), 
                         ('page-break-before', 'avoid'), 
                         ('page-break-inside', 'avoid')):

                value = get(k)
                if value == v:
                    del node.attrib[k]

            for attr in ('margin-left', 'margin-right', 'margin-top', 'margin-bottom',
                         'padding-left', 'padding-right', 'padding-top', 'padding-bottom'):

                value = get(attr)
                if value == '0':
                    node.attrib[attr] = '0em'

            if get('page-break-after') == 'always':
                del node.attrib['page-break-after']
                node.attrib['break-after'] = 'page'

            if get('text-transform'):
                del node.attrib['text-transform']
                
        fo_text = tostring(E.getroot())
        fo_text = fo_text.replace('<ns0:block ' , '<ns0:block margin-top="0" margin-bottom="0" ')  # avoid a linebreak through <li><p> (XFC)
        fo_text = fo_text.replace('<ns0:block/>', '') # causes a crash with XINC    
        fo_text = fo_text.replace('<ns0:block margin-top="0" margin-bottom="0" />', '') 

        open(fo_filename, 'wb').write(fo_text)
        return fo_filename

