=======================================
A Python interface to XSL-FO libraries. 
=======================================

The packages help to convert HTML to PDF, RTF, ODT, DOCX and WML using
XSL-FO technology.


Requirements:
-------------

  - Java 1.5.0 or higher

  - csstoxslfo (included)

  - `XFC-4.0`__ (XMLMind) for ODT, RTF, DOCX and WML support

__ http://www.xmlmind.com

  - `XINC 2.0`__ (Lunasil) for PDF support

__ http://www.lunasil.com

  - `mxTidy`__ (egenix-experimental package from www.egenix.com)

__ http://www.egenix.com
   
  - ElementTree

Installation:
-------------

  - install **zopyx.convert** either using easy_install or by downloading the sources from the Python Cheeseshop
            
  - the environment variable *$XFC_DIR* must be set and point to the root of your XFC installation directory
    
  - the environment variable *$XINC_HOME* must be set and to point to the root of your XINC installation directory


Subversion repository:
----------------------

  - http://svn-public.zopyx.com/viewvc/python-projects/zopyx.convert/trunk/


Usage:
------

Some examples from the Python command-line::

  > from zopyx.convert import Converter
  > C = Convert('/path/to/some/file.html')
  > pdf_filename = C('pdf')
  > rtf_filename = C('rtf')
  > pdt_filename = C('odt')
  > wml_filename = C('wml')
  > docx_filename = C('docx')

A very simple command-line converter is also available::

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
------

zopyx.convert was written by Andreas Jung for ZOPYX Ltd. & Co. KG, Tuebingen, Germany.


License
-------

zopyx.convert is published under the Lesser GNU Public License V 2.1 (LGPL 2.1).
See LICENSE.txt.


Contact
-------

| ZOPYX Ltd. & Co. KG
| c/o Andreas Jung, 
| Charlottenstr. 37/1
| D-72070 Tuebingen, Germany
| E-mail: info at zopyx dot com
| Web: http://www.zopyx.com
