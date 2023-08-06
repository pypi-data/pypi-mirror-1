### -*- coding: utf-8 -*- #############################################
# Разработано компанией Ключевые Решения (http://keysolutions.ru/)
# Все права защищены, 2006-2007
#
# Developed by Key Solutions (http://keysolutions.ru/)
# All right reserved, 2006-2007
#######################################################################
"""Antimat class for the textguard package

$Id: antimat.py 23861 2007-11-25 00:13:00Z xen $
"""
__author__  = "Anatoly Zaretsky"
__license__ = "ZPL"
__version__ = "$Revision: 23861 $"
__date__ = "$Date: 2007-11-25 02:13:00 +0200 (Sun, 25 Nov 2007) $"
__credits__ = "Ilya Soldatkin, arc <at> tcen.ru -- original Perl module Lingua::RU::Antimat, http://www.tcen.ru/antimat"

import re
import os.path
from inspect import isfunction


_ANTI_FILE = os.path.join(os.path.dirname(__file__), 'antiutf8')

anti = re.compile(ur'(?:\b|(?<=_))(?:%s)(?:\b|(?=_))' % open(_ANTI_FILE).read().decode('utf-8'), flags=re.U | re.I)


def remove_slang(repl, slang, count=0):
    if isfunction(repl):
        real_repl = lambda m: repl(m.group(0))
    else:
        real_repl = repl
    return anti.sub(real_repl, string, count)


def detect_slang(slang):
    return anti.match(slang)
