# Copyright (C) 2005 by Dr. Dieter Maurer, Eichendorffstr. 23, D-66386 St. Ingbert, Germany
# see "LICENSE.txt" for details
#       $Id: zpdb.py,v 1.1.1.1 2007/10/05 15:35:36 dieter Exp $
'''Debugger understanding Zopes additional debugging info.'''

from pdb import set_trace, post_mortem, pm

from dm.reuse import rebindFunction

from zExceptions.ExceptionFormatter import TextExceptionFormatter

from dmpdb import Pdb

class Pdb(Pdb, TextExceptionFormatter):
  '''Debugger understanding Zopes additional debugging info.'''
  def __init__(self, *args, **kw):
    super(Pdb, self).__init__(*args, **kw)
    TextExceptionFormatter.__init__(self)

  def getAdditionalFrameInfo(self, frame_lineno):
    info = []
    frame, lineno = frame_lineno
    locals = frame.f_locals
    globals = frame.f_globals
    tbs = locals.get('__traceback_supplement__')
    if tbs is None: tbs = globals.get('__traceback_supplement__')
    if tbs is not None:
      info.extend(self.formatSupplement(tbs[0](*tbs[1:]),
                                        _Object(tb_lineno=lineno)
                                        )
                  )
    tbi = locals.get('__traceback_info__')
    if tbi is not None:
      info.append(self.formatTracebackInfo(tbi))
    return info
    

set_trace = rebindFunction(set_trace, Pdb=Pdb)
post_mortem = rebindFunction(post_mortem, Pdb=Pdb)
pm = rebindFunction(pm, post_mortem=post_mortem)


class _Object(object):
  def __init__(self, **kw):
    self.__dict__.update(kw)
