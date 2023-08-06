"""
pyspread config file
====================

"""

"""
------------
Program info
------------

"""

DEBUG = False # Print debug messages.
VERSION = "0.0.10b" # The current version of pyspread

"""
-----
Paths
-----

Provides paths for libraries and icons

"""

import wx
import os.path

LIBPREFIX = ICONPREFIX = os.path.dirname(__file__) + '/'

try:
    f = open(LIBPREFIX + 'pyspread.py', 'r')
    f.close()
except IOError:
    LIBPREFIX = './'

try:
    f = open(ICONPREFIX + 'icons/pyspread.png', 'r')
    f.close()
except IOError:
    ICONPREFIX = './'

"""
------------------
Key press behavior
------------------

Defines, what actions are mapped on which key for the main window

"""

keyfuncs = {"Ctrl+A": "MainGrid.SelectAll",\
            "\x7f": "MainGrid.delete"} # Del key

# Not needed because of menu:
#            "not_Shift+Ctrl+C": "OnCopy", \
#            "Shift+Ctrl+C": "OnCopyResult",\
#            "Ctrl+V": "OnPaste",\
#            "Ctrl+X": "OnCut",\


"""
----------
font faces
----------

Provides fontfaces for the StyledTextCtrl for different platforms

"""

if wx.Platform == '__WXMSW__':
    faces = { 'times': 'Times New Roman',
              'mono' : 'Courier New',
              'helv' : 'Arial',
              'other': 'Comic Sans MS',
              'size' : 10,
              'size2': 8,
             }
elif wx.Platform == '__WXMAC__':
    faces = { 'times': 'Times New Roman',
              'mono' : 'Monaco',
              'helv' : 'Arial',
              'other': 'Comic Sans MS',
              'size' : 12,
              'size2': 10,
             }
else:
    faces = { 'times': 'Times',
              'mono' : 'Courier',
              'helv' : 'Helvetica',
              'other': 'new century schoolbook',
              'size' : 12,
              'size2': 10,
             }

"""
---------
icontheme
---------

Provides the dict 'icons' with paths to the toolbar icons.

"""

icon_size = (36, 36)
icons = {"FileNew": ICONPREFIX + "icons/actions/filenew.png", \
         "FileOpen": ICONPREFIX + "icons/actions/fileopen.png", \
         "FileSave": ICONPREFIX + "icons/actions/filesave.png", \
         "FilePrint": ICONPREFIX + "icons/actions/fileprint.png", \
         "EditCut": ICONPREFIX + "icons/actions/edit-cut.png", \
         "EditCopy": ICONPREFIX + "icons/actions/edit-copy.png", \
         "EditCopyRes": ICONPREFIX + "icons/actions/edit-copy-results.png", \
         "EditPaste": ICONPREFIX + "icons/actions/edit-paste.png",
         "Undo": ICONPREFIX + "icons/actions/edit-undo.png",
         "Redo": ICONPREFIX + "icons/actions/edit-redo.png",
         "Find": ICONPREFIX + "icons/actions/edit-find.png",
         "FindReplace": ICONPREFIX + "icons/actions/edit-find-replace.png",}

