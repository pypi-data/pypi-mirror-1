"""

  wxAnyThread:  allow methods on wxPython objects to be called from any thread

In wxPython, methods that alter the state of the GUI are only safe to call from
the thread running the main event loop.  Other threads must typically post
events to the GUI thread instead of invoking methods directly.

This module provides an easy way to invoke wxPython object methods safely
from any thread.  Basically, the standard event-based solution is wrapped
into a decorator named "anythread", which can be applied to methods to make
them safe to call from any thread, like so:

  class MyFrame(wx.Frame):

     @anythread
     def ShowFancyStuff():
         ...does some GUI manipulation...

The ShowFancyStuff method can now be directly invoked from any thread.
The thread will block while the main GUI thread performs the method.

"""

__ver_major__ = 0
__ver_minor__ = 1
__ver_patch__ = 0
__ver_sub__ = ""
__version__ = "%d.%d.%d%s" % (__ver_major__,__ver_minor__,
                              __ver_patch__,__ver_sub__)

import wx
import threading

_EVT_INVOKE_METHOD = wx.NewId()

class MethodInvocationEvent(wx.PyEvent):
    """Event fired to the GUI thread indicating a method invocation."""

    def __init__(self,func,args,kwds):
      wx.PyEvent.__init__(self)
      self.SetEventType(_EVT_INVOKE_METHOD)
      self.func = func
      self.args = args
      self.kwds = kwds
      self.blocker = threading.Semaphore(0)

    def invoke(self):
        wx.PostEvent(self.args[0],self)
        self.blocker.acquire()
        return self.result

    def begin(self):
        return self.func(*self.args,**self.kwds)

    def finish(self,result):
        self.result = result
        self.blocker.release()

    def process(self):
        self.finish(self.begin())

def handler(evt):
    evt.process()

def anythread(func):
    """Method decorator allowing call from any thread.
    The method is replaced by one that posts a MethodInvocationEvent to the
    object, then blocks waiting for it to be completed.  The target object
    if automatically connected to the _EVT_INVOKE_METHOD event.
    """
    def invoker(*args,**kwds):
      self = args[0]
      if not hasattr(self,"_AnyThread__connected"):
        self.Connect(-1,-1,_EVT_INVOKE_METHOD,handler)
        self._AnyThread__connected = True
      evt = MethodInvocationEvent(func,args,kwds)
      return evt.invoke()
    return invoker


