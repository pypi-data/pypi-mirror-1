import sys
import pdb
from bdb import BdbQuit
from thread import get_ident
from ZPublisher.Publish import call_object

# global counter for which freeze we're on
freeze_count = 0
# global flag for whether the freeze has been hit
freeze_pending = False
# file and line to stop on
freeze_file = None
freeze_line = None

# per-thread counter for which freeze has had a trace set
trace_up_to_date = {}

def set_freeze(filename=None, lineno=None):
    global freeze_pending, freeze_count, freeze_file, freeze_line
    freeze_pending = True
    freeze_count += 1
    freeze_file = filename
    freeze_line = lineno

def is_trace_up_to_date():
    """
    Returns true if the current thread already has a trace set for
    the most recent freeze.
    """
    return trace_up_to_date.get(get_ident(), 0) == freeze_count

class Fdb(pdb.Pdb):
    """
    Subclass the standard debugger to:
     * only set and dispatch trace if the thread's freeze_pending flag is on
     * allow initially set a breakpoint rather than startting stepping
     * clear the freeze_pending flag *for all threads* once the breakpoint is hit
    """
    
    # per-instance flag for keeping track of whether we've successfully hit the freezepoint
    freeze_active = False
    
    def set_trace(self, frame=None, filename=None, lineno=None):
        """
        Sets a trace if this thread doesn't have one yet and there is a freeze pending.
        """
        if not freeze_pending or is_trace_up_to_date():
            return
        
        if frame is None:
            frame = sys._getframe().f_back
        self.reset()
        while frame:
            # not sure why our callers need a trace function set when we're
            # setting a global one...this was causing problems when continuing
            # back into those callers (publish loop) when a breakpoint was still set
            #frame.f_trace = self.trace_dispatch
            self.botframe = frame
            frame = frame.f_back
        
        if filename is not None and lineno is not None:
            self.set_break(filename, lineno, temporary=1)
            self.set_continue()
        else:
            self.clear_freeze()
            self.set_step()
        sys.settrace(self.trace_dispatch)
        
        trace_up_to_date[get_ident()] = freeze_count

    def trace_dispatch(self, frame, event, arg):
        """
        Stop tracing if some other thread handled the freeze.
        """
        if not freeze_pending or not is_trace_up_to_date():
            if not self.freeze_active:
                self.set_quit()
        return pdb.Pdb.trace_dispatch(self, frame, event, arg)
    
    def clear_break(self, filename, lineno):
        self.clear_freeze()
        return pdb.Pdb.clear_break(self, filename, lineno)
    
    def clear_freeze(self):
        global freeze_pending
        freeze_pending = False
        self.freeze_active = True

def set_thread_trace_when_object_called(object, args, request):
    if freeze_pending and trace_up_to_date.get(get_ident(), 0) < freeze_count:
        if freeze_file is not None and freeze_line is not None:
            Fdb().set_trace(filename=freeze_file, lineno=freeze_line)
        else:
            global freeze_pending
            freeze_pending = False
            return pdb.runcall(object, *args)
    try:
        return call_object(object, args, request)
    except BdbQuit:
        return 'Request cancelled by quitting pdb.  Try the continue (c) command instead if you want the page to finish rendering.'
