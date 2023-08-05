# Copyright (C) 2007-2008 by Dr. Dieter Maurer, Illtalstr. 25, D-66571 Bubach, Germany
# see "LICENSE.txt" for details
#       $Id: __init__.py,v 1.1.1.1 2008/01/01 10:00:39 dieter Exp $
'''Tools to access historical ZODB state.

Will not work with ZODB 3.2, tested with ZODB 3.4 (may work with later
ZODB releases).
'''
from DateTime import DateTime

from connection import Connection

def getObjectAt(obj, time):
  '''return *obj* as it has been at *time*.

  *time* may be a 'DateTime' object or a time in seconds since epoch
  (or a serial/transactionid).

  *obj* and all (direct or indirect) persistent references are
  as of *time*.

  Raises 'POSKeyError' when the state cannot be found.
  '''
  c = Connection(obj._p_jar, time)
  return c[obj._p_oid]


def getHistory(obj, first=0, last=20):
  '''return history records for *obj* between *first* and *last* (indexes).

  The result is a sequence of dicts with "speaking" keys.
  '''
  try: parent = obj.aq_inner.aq_parent
  except AttributeError: parent = None
  oid = obj._p_oid; jar = obj._p_jar
  history = jar.db().history(oid, None, last)[first:]
  for d in history:
    d['time'] = DateTime(d['time'])
    hObj = getObjectAt(obj, d['tid'])
    if parent is not None and hasattr(hObj, '__of__'):
      hObj = hObj.__of__(parent)
    d['obj'] = hObj
  return history
  
