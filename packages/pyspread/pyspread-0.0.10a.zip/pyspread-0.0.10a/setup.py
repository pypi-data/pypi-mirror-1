#!/usr/bin/env python

from distutils.core import setup
from distutils.sysconfig import get_python_lib

setup(name='pyspread',
      version='0.0.10a',
      description='A spreadsheet that accepts a pure python expression in each cell.',
      license='GPL v3 :: GNU General Public License',
      classifiers=[ 'Development Status :: 3 - Alpha',
                    'Intended Audience :: End Users/Desktop',
      ],
      author='Martin Manns',
      author_email='mmanns@gmx.net',
      url='http://sourceforge.net/projects/pyspread/',
      requires=['numpy (>=1.1)', 'wx (>=2.7)'],
      scripts=['pyspread/pyspread.py'],
      packages=['pyspread'],
      package_dir={'pyspread': 'pyspread'},
#      py_modules=['pyspread', 'config', '_choicebars', '_datastructures',\
#                  '_interfaces', '_widgets', '_dialogs'],
      package_data={'pyspread': ['icons/*.png', 'icons/actions/*.png', \
                         'examples/*', \
                         'doc/manual.html', 'README', 'COPYING']},
)

import distutils.sysconfig
try:
    pthfile = open(get_python_lib() + "/pyspread.pth", 'w')
    pthfile.write("pyspread")
    pthfile.close()
except IOError:
    print 'Creation of ' + distutils.sysconfig.get_python_lib() + ' pyspread.pth failed.'
