"""
pyspread config file
====================

"""

"""
Program info
============

"""

VERSION = "0.0.11" # The current version of pyspread

"""
Command line defaults
=====================

"""

default_dimensions = (1000, 100, 3) # Used for empty sheet at start-up

"""
Paths
=====

Provides paths for libraries and icons

"""

import os.path

import wx
import wx.stc  as  stc

ICONPREFIX = os.path.dirname(os.path.realpath(__file__)) + '/'


"""
CSV
===

CSV import options

"""

# Number of bytes for the sniffer (should be larger than 1st+2nd line)
SNIFF_SIZE = 65536 


"""
Key press behavior
==================

Defines, what actions are mapped on which key for the main window

"""

KEYFUNCTIONS = {"Ctrl+A": "MainGrid.SelectAll",\
                "\x7f": "MainGrid.delete"} # Del key

# Not needed because of menu:
#            "not_Shift+Ctrl+C": "OnCopy", \
#            "Shift+Ctrl+C": "OnCopyResult",\
#            "Ctrl+V": "OnPaste",\
#            "Ctrl+X": "OnCut",\


"""
StyledTextCtrl layout
=====================

Provides layout for the StyledTextCtrl widget that is used in the macro dialog

Platform dependent layout is specified here.

"""

"""
Font faces
----------

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
Fold symbols
------------

The following styles are pre-defined:
  "arrows"      Arrow pointing right for contracted folders,
                arrow pointing down for expanded
  "plusminus"   Plus for contracted folders, minus for expanded
  "circletree"  Like a flattened tree control using circular headers 
                and curved joins
  "squaretree"  Like a flattened tree control using square headers

"""

fold_symbol_styles = { \
  "arrows": \
  [ \
    (stc.STC_MARKNUM_FOLDEROPEN, stc.STC_MARK_ARROWDOWN, "black", "black"), \
    (stc.STC_MARKNUM_FOLDER, stc.STC_MARK_ARROW, "black", "black"), \
    (stc.STC_MARKNUM_FOLDERSUB, stc.STC_MARK_EMPTY, "black", "black"), \
    (stc.STC_MARKNUM_FOLDERTAIL, stc.STC_MARK_EMPTY, "black", "black"), \
    (stc.STC_MARKNUM_FOLDEREND, stc.STC_MARK_EMPTY, "white", "black"), \
    (stc.STC_MARKNUM_FOLDEROPENMID, stc.STC_MARK_EMPTY, "white", "black"), \
    (stc.STC_MARKNUM_FOLDERMIDTAIL, stc.STC_MARK_EMPTY, "white", "black"), \
  ], \
  "plusminus": \
  [ \
    (stc.STC_MARKNUM_FOLDEROPEN, stc.STC_MARK_MINUS, "white", "black"), \
    (stc.STC_MARKNUM_FOLDER, stc.STC_MARK_PLUS,  "white", "black"), \
    (stc.STC_MARKNUM_FOLDERSUB, stc.STC_MARK_EMPTY, "white", "black"), \
    (stc.STC_MARKNUM_FOLDERTAIL, stc.STC_MARK_EMPTY, "white", "black"), \
    (stc.STC_MARKNUM_FOLDEREND, stc.STC_MARK_EMPTY, "white", "black"), \
    (stc.STC_MARKNUM_FOLDEROPENMID, stc.STC_MARK_EMPTY, "white", "black"), \
    (stc.STC_MARKNUM_FOLDERMIDTAIL, stc.STC_MARK_EMPTY, "white", "black"), \
  ], \
  "circletree":
  [ \
    (stc.STC_MARKNUM_FOLDEROPEN, stc.STC_MARK_CIRCLEMINUS, "white", "#404040"), \
    (stc.STC_MARKNUM_FOLDER, stc.STC_MARK_CIRCLEPLUS, "white", "#404040"), \
    (stc.STC_MARKNUM_FOLDERSUB, stc.STC_MARK_VLINE, "white", "#404040"), \
    (stc.STC_MARKNUM_FOLDERTAIL, stc.STC_MARK_LCORNERCURVE, "white", "#404040"), \
    (stc.STC_MARKNUM_FOLDEREND, stc.STC_MARK_CIRCLEPLUSCONNECTED, "white", "#404040"), \
    (stc.STC_MARKNUM_FOLDEROPENMID, stc.STC_MARK_CIRCLEMINUSCONNECTED, "white", "#404040"), \
    (stc.STC_MARKNUM_FOLDERMIDTAIL, stc.STC_MARK_TCORNERCURVE, "white", "#404040"), \
  ], \
  "squaretree": 
  [ \
    (stc.STC_MARKNUM_FOLDEROPEN, stc.STC_MARK_BOXMINUS, "white", "#808080"), \
    (stc.STC_MARKNUM_FOLDER, stc.STC_MARK_BOXPLUS, "white", "#808080"), \
    (stc.STC_MARKNUM_FOLDERSUB, stc.STC_MARK_VLINE, "white", "#808080"), \
    (stc.STC_MARKNUM_FOLDERTAIL, stc.STC_MARK_LCORNER, "white", "#808080"), \
    (stc.STC_MARKNUM_FOLDEREND, stc.STC_MARK_BOXPLUSCONNECTED, "white", "#808080"), \
    (stc.STC_MARKNUM_FOLDEROPENMID, stc.STC_MARK_BOXMINUSCONNECTED, "white", "#808080"), \
    (stc.STC_MARKNUM_FOLDERMIDTAIL, stc.STC_MARK_TCORNER, "white", "#808080"), \
  ] \
}

fold_symbol_style = fold_symbol_styles["circletree"]

"""
Text styles
-----------

The lexer defines what each style is used for, we just have to define
what each style looks like.  The Python style set is adapted from Scintilla
sample property files.

"""

text_styles = [ \
  (stc.STC_STYLE_DEFAULT, "face:%(helv)s,size:%(size)d" % faces), \
  (stc.STC_STYLE_LINENUMBER, "back:#C0C0C0,face:%(helv)s,size:%(size2)d" % faces), \
  (stc.STC_STYLE_CONTROLCHAR, "face:%(other)s" % faces), \
  (stc.STC_STYLE_BRACELIGHT, "fore:#FFFFFF,back:#0000FF,bold"), \
  (stc.STC_STYLE_BRACEBAD, "fore:#000000,back:#FF0000,bold"), \
  # Python styles
  # Default 
  (stc.STC_P_DEFAULT, "fore:#000000,face:%(helv)s,size:%(size)d" % faces), \
  # Comments
  (stc.STC_P_COMMENTLINE, "fore:#007F00,face:%(other)s,size:%(size)d" % faces), \
  # Number
  (stc.STC_P_NUMBER, "fore:#007F7F,size:%(size)d" % faces), \
  # String
  (stc.STC_P_STRING, "fore:#7F007F,face:%(helv)s,size:%(size)d" % faces), \
  # Single quoted string
  (stc.STC_P_CHARACTER, "fore:#7F007F,face:%(helv)s,size:%(size)d" % faces), \
  # Keyword
  (stc.STC_P_WORD, "fore:#00007F,bold,size:%(size)d" % faces), \
  # Triple quotes
  (stc.STC_P_TRIPLE, "fore:#7F0000,size:%(size)d" % faces), \
  # Triple double quotes
  (stc.STC_P_TRIPLEDOUBLE, "fore:#7F0000,size:%(size)d" % faces), \
  # Class name definition
  (stc.STC_P_CLASSNAME, "fore:#0000FF,bold,underline,size:%(size)d" % faces), \
  # Function or method name definition
  (stc.STC_P_DEFNAME, "fore:#007F7F,bold,size:%(size)d" % faces), \
  # Operators
  (stc.STC_P_OPERATOR, "bold,size:%(size)d" % faces), \
  # Identifiers
  (stc.STC_P_IDENTIFIER, "fore:#000000,face:%(helv)s,size:%(size)d" % faces), \
  # Comment-blocks
  (stc.STC_P_COMMENTBLOCK, "fore:#7F7F7F,size:%(size)d" % faces), \
  # End of line where string is not closed
  (stc.STC_P_STRINGEOL, "fore:#000000,face:%(mono)s,back:#E0C0E0,eol,size:%(size)d" % faces), \
]

"""
Icontheme
=========

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

