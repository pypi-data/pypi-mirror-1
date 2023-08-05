# Configuration variables
NAME     = '4Suite-XML'
VERSION  = '1.0.1'
FULLNAME = '4Suite-XML-1.0.1'
URL      = 'http://4suite.org/'

import sys
if getattr(sys, 'frozen', False):
    # "bundled" installation locations (e.g., py2exe, cx_Freeze)
    RESOURCEBUNDLE = True
    PYTHONLIBDIR   = '\\'
    BINDIR         = None
    DATADIR        = '\\Share'
    SYSCONFDIR     = None
    LOCALSTATEDIR  = None
    LIBDIR         = None
    LOCALEDIR      = '\\Share\\Locale'
else:
    # standard distutils installation directories
    RESOURCEBUNDLE = True
    PYTHONLIBDIR   = '\\'
    BINDIR         = None
    DATADIR        = '\\Share'
    SYSCONFDIR     = None
    LOCALSTATEDIR  = None
    LIBDIR         = None
    LOCALEDIR      = '\\Share\\Locale'
del sys
