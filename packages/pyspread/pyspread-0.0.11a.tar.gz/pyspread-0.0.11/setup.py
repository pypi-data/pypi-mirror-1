#!/usr/bin/env python

from distutils.core import setup
from distutils.sysconfig import get_python_lib

setup(name='pyspread',
      version='0.0.11',
      description='A spreadsheet that accepts a pure python expression in each cell.',
      license='GPL v3 :: GNU General Public License',
      classifiers=[ 'Development Status :: 3 - Alpha',
                    'Environment :: MacOS X',
                    'Environment :: Win32 (MS Windows)',
                    'Environment :: X11 Applications :: GTK',
                    'Intended Audience :: End Users/Desktop',
                    'License :: OSI Approved :: GNU General Public License (GPL)',
                    'Natural Language :: English',
                    'Operating System :: OS Independent',
                    'Programming Language :: Python :: 2.4',
                    'Programming Language :: Python :: 2.5',
                    'Topic :: Office/Business :: Financial :: Spreadsheet',
      ],
      author='Martin Manns',
      author_email='mmanns@gmx.net',
      url='http://pyspread.sourceforge.net',
      install_requires=["numpy>=1.1", "networkx>=0.99"],
      requires=['numpy (>=1.1)', 'wx (>=2.8.7)', 'networkx (>=0.99)'],
      scripts=['pyspread/pyspread'],
      packages=['pyspread'],
      package_data={'pyspread': ['icons/*.png', 'icons/actions/*.png', \
                         'examples/*', \
                         'doc/manual.html', 'README', 'COPYING']},
)
