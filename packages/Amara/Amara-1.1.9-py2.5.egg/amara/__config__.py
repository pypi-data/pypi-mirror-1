# Configuration variables
NAME     = 'Amara'
VERSION  = '1.1.9'
FULLNAME = 'Amara-1.1.9'
URL      = 'http://uche.ogbuji.net/tech/4suite/amara/'

import sys
if getattr(sys, 'frozen', False):
    # "bundled" installation locations (e.g., py2exe, cx_Freeze)
    RESOURCEBUNDLE = True
    PYTHONLIBDIR   = '/'
    BINDIR         = None
    DATADIR        = '/Share'
    SYSCONFDIR     = None
    LOCALSTATEDIR  = None
    LIBDIR         = None
    LOCALEDIR      = '/Share/Locale'
else:
    # standard distutils installation directories
    RESOURCEBUNDLE = True
    PYTHONLIBDIR   = '/'
    BINDIR         = None
    DATADIR        = '/Share'
    SYSCONFDIR     = None
    LOCALSTATEDIR  = None
    LIBDIR         = None
    LOCALEDIR      = '/Share/Locale'
del sys
