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
desc = open(readme_file).read() 

changes_file = os.path.join('src', 'zopyx', 'convert', 'CHANGES.txt')
changes = open(changes_file).read()

long_description = desc + '\nChanges:\n========\n\n' + changes


setup(name='zopyx.convert',
      version=version,
      license='ZPL (see LICENSE.txt)',
      author='Andreas Jung',
      author_email='info@zopyx.com',
      maintainer='Andreas Jung',
      maintainer_email='info@zopyx.com',
      classifiers=CLASSIFIERS,
#      url='http://svn.zope.org/zopyx.convert/tags/%s' % version,
      description='A Python interface XSL-FO libraries',
      long_description=long_description,
      packages=find_packages('src'),
      package_dir = {'': 'src'},
      include_package_data = True,
      zip_safe=True,
      install_requires=['setuptools'],
      namespace_packages=['zopyx'],
#      entry_points={'console_scripts': ['convertlayer = zopyx.convert.cli:main',]},
      )                       
