##########################################################################
# zopyx.convert - XSL-FO related functionalities
#
# (C) 2007, ZOPYX Ltd & Co. KG, Tuebingen, Germany
##########################################################################

import os
from setuptools import setup, find_packages


CLASSIFIERS = [
    'Programming Language :: Python',
]

version_file = os.path.join('src', 'zopyx', 'convert', 'version.txt')
version = open(version_file).read().strip()

readme_file = os.path.join('src', 'zopyx', 'convert', 'README.txt')
desc = open(readme_file).read().strip()

changes_file = os.path.join('src', 'zopyx', 'convert', 'CHANGES.txt')
changes = open(changes_file).read().strip()

long_description = desc + '\n\nChanges:\n========\n\n' + changes


setup(name='zopyx.convert',
      version=version,
      license='ZPL (see LICENSE.txt)',
      author='Andreas Jung',
      author_email='info@zopyx.com',
      maintainer='Andreas Jung',
      maintainer_email='info@zopyx.com',
      classifiers=CLASSIFIERS,
      url='http://cheeseshop.python.org/pypi/zopyx.convert',
      description='A Python interface to XSL-FO libraries (Conversion HTML to PDF, RTF, DOCX, WML and ODT)',
      long_description=long_description,
      packages=['zopyx', 'zopyx.convert'],
      package_dir = {'': 'src'},
      include_package_data = True,
      zip_safe=False,
      install_requires=['setuptools', 'elementtree', 'beautifulsoup'],
      namespace_packages=['zopyx'],
      entry_points={'console_scripts': ['xslfo-convert = zopyx.convert.cli:main',]},
      )                       
