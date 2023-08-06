### -*- coding: utf-8 -*- #############################################
# Разработано компанией Ключевые Решения (http://keysolutions.ru/)
# Все права защищены, 2006-2007
#
# Developed by Key Solutions (http://keysolutions.ru/)
# All right reserved, 2006-2007                                                                 #
#######################################################################
"""TSTypes

$Id: tstypes.py 23861 2007-11-25 00:13:00Z xen $
"""
__author__  = "Anatoly Bubenkov"
__license__ = "ZPL"
__version__ = "$Revision: 23861 $"
__date__ = "$Date: 2007-11-25 02:13:00 +0200 (Sun, 25 Nov 2007) $"

from threading import RLock, Lock

class TSDict(dict):
  def __init__(self):
    self.lock_obj = RLock()

  def lock(self):
    return self.lock_obj.acquire()

  def unlock(self):
    return self.lock_obj.release()

class TSList(list):
  def __init__(self):
    self.lock_obj = RLock()

  def lock(self):
    return self.lock_obj.acquire()

  def unlock(self):
    return self.lock_obj.release()

class TSObject(object):

  def __init__(self, value = None):
    self.lock_obj = RLock()
    self._value = value

  def lock(self):
    return self.lock_obj.acquire()

  def unlock(self):
    return self.lock_obj.release()

  def _getValue(self):
    return self._value

  def _setValue(self, value):
    self._value = value

  value = property(_getValue, _setValue)
