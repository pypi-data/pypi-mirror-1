"""$URL: svn+ssh://svn.mems-exchange.org/repos/trunk/dulcinea/lib/script_util.py $
$Id: script_util.py 27178 2005-08-10 14:24:17Z dbinger $
"""

import sys, os, time, pdb
from optparse import OptionParser

class Debugger(pdb.Pdb):
    """
    Calling the constructor of this class puts you in the
    interactive debugger.  This is like pdb.post_mortem, except
    that the traceback is printed and the exit command works.
    """
    def __init__(self):
        pdb.Pdb.__init__(self)
        (exc_type, exc_value, tb) = sys.exc_info()
        up = 0
        if tb is None:
            try:
                raise
            except:
                (exc_type, exc_value, tb) = sys.exc_info()
            down = 1
        self.reset()
        while tb.tb_next is not None:
            tb = tb.tb_next
        self.interaction(tb.tb_frame, tb)

    def interaction(self, frame, traceback):
        self.setup(frame, traceback)
        self.curindex = self.curindex - 1
        self.curframe = self.stack[self.curindex][0]
        self.lineno = None
        self.do_explain()
        self.cmdloop()
        self.forget()

    def do_explain(self, arg=None):
        print "\n"
        for stack_entry in self.stack[self.curindex-3:-1]:
            self.print_stack_entry(stack_entry)
        print
        self.do_args(None)
        print
        self.do_list("%s,13" % (self.curframe.f_lineno - 12))

    def help_explain(self):
        print """
Print a slice of the stack, args to this function, and list the list the
section of code being executed.
"""

    def do_exit(self, arg):
        os._exit(1)

    def help_exit(self):
        print """Terminate this process."""


def _verbose(arg, _depth=1):
    """Print arg, eval(arg), and then report the time it took."""
    frame = sys._getframe(_depth)
    start = time.time()
    print arg
    result = eval(arg, frame.f_globals, frame.f_locals)
    finish = time.time()
    print '%s completed in %1.3f seconds.' % (arg, finish-start)
    return result

def _verbose_catch(arg):
    """
    Like verbose(), but drop into the debugger
    on exceptions.
    """
    try:
        _verbose(arg, _depth=2)
    except SystemExit:
        raise
    except:
        print arg, 'FAILED'
        Debugger()

def verbose_main(fun):
    """
    verbose_main parses a command line and calls fun
    with a first argument set to either verbose
    or else to verbose_catch.
    Command line arguments not declared as options here are passed on
    as arguments to fun.
    """
    usage = "usage: %prog [options] [dbfile]"
    parser = OptionParser(usage)
    parser.add_option("-c", "--catch-errors", action="store_true",
                      help=("catch exceptions from update code and "
                            "drop into pdb (default: let it crash"))
    (options, args) = parser.parse_args()

    if options.catch_errors:
        fun(_verbose_catch, *args)
    else:
        fun(_verbose, *args)

def no_rerun(root, release_id):
    if root.get('version') == release_id:
        print "This update has already been executed."
        raise SystemExit
    else:
        root['version'] = release_id
