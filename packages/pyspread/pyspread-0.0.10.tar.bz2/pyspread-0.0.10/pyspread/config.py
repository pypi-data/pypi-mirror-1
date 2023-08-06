"""
pyspread config file
====================

"""

import wx
import distutils.sysconfig

LIBPREFIX = distutils.sysconfig.get_python_lib() + '/pyspread/'
try:
    f = open(LIBPREFIX + 'pyspread.py', 'r')
    f.close()
except IOError:
    LIBPREFIX = './'

DEBUG = False

VERSION = "0.0.10"

"""
faces
=====

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
icontheme
=========

Provides the dict 'icons' with paths to the toolbar icons.

"""

# Toolbar items

icon_size = (36, 36)
icons = {"FileNew": LIBPREFIX + "icons/actions/filenew.png", \
         "FileOpen": LIBPREFIX + "icons/actions/fileopen.png", \
         "FileSave": LIBPREFIX + "icons/actions/filesave.png", \
         "FilePrint": LIBPREFIX + "icons/actions/fileprint.png", \
         "EditCut": LIBPREFIX + "icons/actions/edit-cut.png", \
         "EditCopy": LIBPREFIX + "icons/actions/edit-copy.png", \
         "EditCopyRes": LIBPREFIX + "icons/actions/edit-copy-results.png", \
         "EditPaste": LIBPREFIX + "icons/actions/edit-paste.png",
         "Undo": LIBPREFIX + "icons/actions/edit-undo.png",
         "Redo": LIBPREFIX + "icons/actions/edit-redo.png",
         "Find": LIBPREFIX + "icons/actions/edit-find.png",
         "FindReplace": LIBPREFIX + "icons/actions/edit-find-replace.png",}
