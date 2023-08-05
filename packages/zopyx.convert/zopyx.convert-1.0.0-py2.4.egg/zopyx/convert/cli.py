##########################################################################
# zopyx.convert - XSL-FO related functionalities
#
# (C) 2007, ZOPYX Ltd & Co. KG, Tuebingen, Germany
##########################################################################


from optparse import OptionParser
from convert import Converter
from config import supported_formats

def convert(options, args):

    for fn in args:
        C = Converter(fn, verbose=options.verbose)
        output_filename = C(options.format, output_filename=options.output_filename)
        print 'Generated file: %s' % output_filename
   

def main():

    parser = OptionParser()
    parser.add_option('-v', '--verbose', dest='verbose', action="store_true",
                      default=False, help='verbose on')

    parser.add_option('-f', '--format', dest='format',
                      help='|'.join(supported_formats))

    parser.add_option('-o', '--output', dest='output_filename',
                      help='output filename')

    (options, args) = parser.parse_args()
    convert(options, args)


if __name__ == '__main__':
    main()
