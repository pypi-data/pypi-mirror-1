##########################################################################
# zopyx.convert - XSL-FO related functionalities
#
# (C) 2007, ZOPYX Ltd & Co. KG, Tuebingen, Germany
##########################################################################

A Python interface to XSL-FO libraries. 

The packages helps to convert HTML to PDF, RTF, ODT, DOCX and WML using
XSL-FO technology.


Requirements:
-------------

  - Java 1.4.0 or higher (1.5.X or 1.6.X are preferred)

  - csstoxslfo (included)

  - XFC-4.0 (www.xmlmind.com) for PDF support

  - XINC 2.0 (www.lunasil.com) for ODT, RTF, DOCX, WML support

  - mxTidy (egenix-experimental package from www.egenix.com)


Installation:
-------------

  - install zopyx.convert either using easy_install or by downloading the sources

  - $XFC_DIR must be set and point to the root of your XFC installation directory
    
  - $XINC_HOME must be set and to point to the root of your XINC installation directory


Subversion repository:
----------------------

  - http://svn-public.zopyx.com/viewvc/python-projects/zopyx.convert/trunk/


Usage:
------

  > from zopyx.convert import Converter
  > C = Convert('/path/to/some/file.html')
  > pdf_filename = C('pdf')
  > rtf_filename = C('rtf')
  > pdt_filename = C('odt')
  > wml_filename = C('wml')
  > docx_filename = C('docx')

  A very simple command-line converter is also available:

  > xslfo-convert --format rtf --output foo.rtf sample.html


How zopyx.convert works internally:
-----------------------------------

  - The source HTML file is converted to XHTML using mxTidy

  - the XHTML file is converted to FO using the great "csstoxslfo" converter
    written by Werner Donne.

  - the FO file is passed either to the external XINC or XFC converter to 
    generated the desired output format

  - all converters are based on Java technology make the conversion solution
    highly portable across operating system (including Windows)
    

Limitations:
------------

  - Works currently only on Linux/Unix, no Windows support so far
 
  - no image support right now (exceptions will be raised)


Why XINC/XFC and not FOP?
-------------------------
zopyx.convert is build on the commercial converters XINC/XFC because these
converters *just work*.  Depending on your needs to must make your choice
between the several available additions. Why not Apache FOP? FOP has been
evaluated in 2004 for the conversion to RTF/PDF and it was pretty much unusable
at that time. Now in 2007 Apache FOP reached version 0.9.3 thinks are looking
better. However open formats like ODT (Open-Office) and DOCX (Microsoft Office
2007) have come up and need to be supported. XFC fills the gap by supporting
RTF, ODT, DOCX and WML. 


Author
======
zopyx.convert was written by Andreas Jung for ZOPYX Ltd. & Co. KG, Tuebingen, Germany.


License
=======
zopyx.convert is published under the Lesser GNU Public License V 2.1 (LGPL 2.1).
See LICENSE.txt.


Contact
=======
Andreas Jung, 
E-mail: info at zopyx dot com
Web: http://www.zopyx.com
