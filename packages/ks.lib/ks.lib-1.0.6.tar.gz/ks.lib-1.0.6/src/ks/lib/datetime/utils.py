### -*- coding: utf-8 -*- #############################################
# Разработано компанией Ключевые Решения (http://keysolutions.ru/)
# Все права защищены, 2006-2007
#
# Developed by Key Solutions (http://keysolutions.ru/)
# All right reserved, 2006-2007
#######################################################################
"""datetime utils for the Zope 3 based ks.lib.datetime package

$Id: utils.py 35252 2007-12-03 18:46:05Z anatoly $
"""
__author__  = "Anatoly Bubenkov"
__license__ = "ZPL"
__version__ = "$Revision: 35252 $"
__date__ = "$Date: 2007-12-03 20:46:05 +0200 (Mon, 03 Dec 2007) $"

import datetime

def timedelta2seconds(value):
    assert isinstance(value, datetime.timedelta)
    return value.days*24*3600 + value.seconds + value.microseconds
