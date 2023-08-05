##########################################################################
# zopyx.convert - XSL-FO related functionalities
#
# (C) 2007, ZOPYX Ltd & Co. KG, Tuebingen, Germany
##########################################################################

import os

from config import supported_formats

from html2fo import html2fo
from fo2xfc import fo2xfc, xfc_available
from fo2pdf import fo2pdf, xinc_available


class Converter(object):
    """High-level OO interface to XSL-FO conversions """

    def __init__(self, filename, cleanup=False):
        self.filename = filename
        self.fo_filename = None        
        self.cleanup = cleanup


    def convert(self, format, output_filename=None):

        if format == 'fo':
            if self.fo_filename is None:
                self.fo_filename = html2fo(self.filename)
            return self.fo_filename

        if not format in supported_formats:
            raise ValueError('Unsupported format: %s' % format)

        if self.fo_filename is None:
            self.fo_filename = html2fo(self.filename)

        if format == 'pdf':
            if not xinc_available:
                raise RuntimeError("The external XINC converter isn't available")
            output_filename = fo2pdf(self.fo_filename, output_filename=output_filename)

        else:
            if not xfc_available:
                raise RuntimeError("The external XFC converter isn't available")
            output_filename = fo2xfc(self.fo_filename, format, output_filename=output_filename)

        return output_filename


    def __call__(self, *args, **kw):
        return self.convert(*args, **kw)

    def __del__(self):
        """ House-keeping """

        if self.cleanup:
            if self.fo_filename:
                os.unlink(self.fo_filename)

