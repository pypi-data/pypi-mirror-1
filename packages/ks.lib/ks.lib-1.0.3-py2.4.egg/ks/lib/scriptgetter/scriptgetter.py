### -*- coding: utf-8 -*- #############################################
# Разработано компанией Ключевые Решения (http://keysolutions.ru/)
# Все права защищены, 2006-2007
#
# Developed by Key Solutions (http://keysolutions.ru/)
# All right reserved, 2006-2007
#######################################################################
"""ScriptGetter module for the scriptgetter package

$Id: scriptgetter.py 23861 2007-11-25 00:13:00Z xen $
"""
__author__  = "Anatoly Bubenkov"
__license__ = "ZPL"
__version__ = "$Revision: 23861 $"
__date__ = "$Date: 2007-11-25 02:13:00 +0200 (Sun, 25 Nov 2007) $"

import os.path
import sys
import re

_ignore = re.compile('^.*(?:py|pyo|pyc|zcml)$')

def getAll(path, ignore):
    return ((i, open(os.path.join(path, i)).read().decode('utf-8'))
                for i in os.listdir(path)
                    if os.path.isfile(os.path.join(path, i))
                    and not ignore(i))

class ScriptHolder(object):

    def __init__(self, path, ignore):
        self.path = path
        self.ignore = ignore

    def __getitem__(self, key):
        return open(os.path.join(self.path, key)).read()

    def items(self):
        return getAll(self.path, self.ignore)

    def __iter__(self):
        return self.keys()

    def keys(self):
        return (key for key, value in getAll(self.path, self.ignore))

def appendAllToPackage(ignore=_ignore.match):
    frame = sys._getframe(1)
    locals = frame.f_locals

    # Try to make sure we were called from a module def
    if (locals is not frame.f_globals) or ('__name__' not in locals):
        raise TypeError(
            "appendAllToPackage can only be used from a module definition.")

    all = ScriptHolder(locals['__path__'][0], ignore)
    for name, value in all.items():
        locals[name] = value
    locals['all'] = all
