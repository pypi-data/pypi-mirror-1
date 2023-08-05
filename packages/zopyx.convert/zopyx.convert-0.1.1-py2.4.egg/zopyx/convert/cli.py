##########################################################################
# zopyx.convert - XSL-FO related functionalities
#
# (C) 2007, ZOPYX Ltd & Co. KG, Tuebingen, Germany
##########################################################################


from optparse import OptionParser

import html2fo
import fo2xfc
import fo2pdf


def convert(options, args):

    for fn in args:
    
        fo_filename = html2fo.html2fo(fn)

        if options.format in ('rtf', 'odt', 'docx', 'wml'):
            output_filename = fo2xfc.fo2xfc(fo_filename, options.format)

        elif options.format == 'pdf':
            output_filename = fo2pdf.fo2pdf(fo_filename)


        else:
            raise ValueError('Unsupported format %s' % options.format)

        print 'Generated file: %s' % output_filename


   

def main():

    parser = OptionParser()
    parser.add_option('-f', '--format', dest='format',
                      help='rtf|pdf|odt|wml|docx')

    parser.add_option('-o', '--output', dest='output_filename',
                      help='output filename')

    (options, args) = parser.parse_args()
    convert(options, args)


if __name__ == '__main__':
    main()
