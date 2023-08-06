#!/usr/bin/env python

from distutils.core import setup
from distutils.sysconfig import get_python_lib

setup(name='pyspread',
      version='0.0.10b',
      description='A spreadsheet that accepts a pure python expression in each cell.',
      license='GPL v3 :: GNU General Public License',
      classifiers=[ 'Development Status :: 3 - Alpha',
                    'Intended Audience :: End Users/Desktop',
      ],
      author='Martin Manns',
      author_email='mmanns@gmx.net',
      url='http://pyspread.sourceforge.net',
      install_requires=["numpy>=1.1"],
      requires=['numpy (>=1.1)', 'wx (>=2.8.7)'],
      scripts=['pyspread/pyspread'],
      packages=['pyspread'],
      package_data={'pyspread': ['icons/*.png', 'icons/actions/*.png', \
                         'examples/*', \
                         'doc/manual.html', 'README', 'COPYING']},
)
