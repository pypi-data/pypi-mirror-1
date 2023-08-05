#!/usr/bin/env python
# -*- coding: iso8859-1 -*-


"""pynakotheka is a simple python script which generates static HTML photo albums.
Released under GNU Public License, read COPYING for more details."""


from distutils.core import setup
from glob import glob
import sys


DOC_FILES = ['COPYING', 'README', 'README.html', 'album.xml.example']
MAN_FILES = ['pynakotheka.1']
TMPL_FILES = []
for tmpl in glob('templates/*'):
    tmpl_contents = glob(tmpl + '/*')
    TMPL_FILES.append(('share/pynakotheka/' + tmpl , tmpl_contents))

classifiers = """\
Development Status :: 5 - Production/Stable
Environment :: Console
Environment :: Win32 (MS Windows)
Intended Audience :: End Users/Desktop
Intended Audience :: System Administrators
License :: OSI Approved :: GNU General Public License (GPL)
Natural Language :: English
Operating System :: POSIX
Operating System :: Unix
Operating System :: MacOS :: MacOS X
Operating System :: Microsoft
Programming Language :: Python
Topic :: Internet :: WWW/HTTP
Topic :: Multimedia :: Graphics
Topic :: Utilities
"""

doclines = __doc__.split("\n")

if sys.version_info < (2, 3):
    _setup = setup
    def setup(**kwargs):
        if kwargs.has_key("classifiers"):
            del kwargs["classifiers"]
        _setup(**kwargs)


setup(name = 'pynakotheka',
      version = '1.0.2',
      license = 'GPL',
      description = doclines[0],
      long_description = '\n'.join(doclines[2:]),
      author = 'Inigo Serna',
      author_email = 'inigoserna@telefonica.net',
      url = 'http://inigo.katxi.org/devel/pynakotheka',
      platforms = 'POSIX',
      classifiers = filter(None, classifiers.split("\n")),
      scripts = ['pynakotheka.py'],
      data_files = [('share/doc/pynakotheka', DOC_FILES),
                    ('share/man/man1', MAN_FILES)] + TMPL_FILES
     )
