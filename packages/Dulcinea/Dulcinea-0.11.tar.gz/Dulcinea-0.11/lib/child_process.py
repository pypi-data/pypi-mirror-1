"""
$URL: svn+ssh://svn.mems-exchange.org/repos/trunk/dulcinea/lib/child_process.py $
$Id: child_process.py 27381 2005-09-13 14:18:55Z dbinger $

Execute a child process and communicate with it using pipes.  This interface
has the following advantages over os.system() and os.popen():

  * The shell is not used for parsing the command line.  This eliminates
    problems with shell meta characters.

  * Pipes to stdin, stdout and stderr are provided.

  * The exit status of the child process is available.
     
"""
import os
import sys

class _ChildProcess:
    """
    Instance attributes:
    
        pid : int
          the process id of the child process
        stdin : file
          open file connected to file descriptor 0 of the child process
        stdout : file
          open file connected to file descriptor 1 of the child process
        stderr : file
          open file connected to file descriptor 2 of the child process
    """

    try:
        MAXFD = os.sysconf('SC_OPEN_MAX')
    except:
        MAXFD = 256

    def __init__(self, argv, bufsize=-1):
        child_stdin, stdin = os.pipe()
        stdout, child_stdout = os.pipe()
        stderr, child_stderr = os.pipe()
        self.stdin = os.fdopen(stdin, 'w', bufsize)
        self.stdout = os.fdopen(stdout, 'r', bufsize)
        self.stderr = os.fdopen(stderr, 'r', bufsize)
        self.pid = os.fork()
        if self.pid == 0:
            exec_error_fd = sys.stderr.fileno()
            # ensure exec_error_fd and friends are not using fds 0-3
            while exec_error_fd < 3:
                exec_error_fd = os.dup(exec_error_fd)
            while child_stdout < 3:
                child_stdout = os.dup(child_stdout)
            while child_stderr < 3:
                child_stderr = os.dup(child_stderr)
            os.dup2(child_stdin, 0)
            os.dup2(child_stdout, 1)
            os.dup2(child_stderr, 2)
            os.dup2(exec_error_fd, 3)
            for i in range(4, self.MAXFD):
                try:
                    os.close(i)
                except:
                    pass
            try:
                os.execvp(argv[0], argv)
            except OSError, err:
                os.write(3, "couldn't exec %s: %s\n" % (argv[0], err.strerror))
            except:
                os.write(3, "couldn't exec %s\n" % argv[0])
            os._exit(1)
        os.close(child_stdin)
        os.close(child_stdout)
        os.close(child_stderr)

    def read(self, n=-1):
        """Read from child stdout"""
        return self.stdout.read(n)

    def readline(self):
        """Readline from child stdout"""
        return self.stdout.readline()

    def readlines(self):
        """Readlines from child stdout"""
        return self.stdout.readlines()

    def write(self, s):
        """Write data to child stdin"""
        self.stdin.write(s)

    def flush(self):
        """Flush stdin pipe to child"""
        self.stdin.flush()

    def close(self):
        """Close stdin, stdout and stderr pipes to child process.  Wait
        for the exit status of the child and return it."""
        for fd in (self.stdin, self.stdout, self.stderr):
            if not fd.closed:
                fd.close()
        status = self.wait()
        if status == 0:
            return None # matches behavior of popen(...).close()
        else:
            return status

    def wait(self, flags=0):
        pid, status = os.waitpid(self.pid, flags)
        return status


def execute(argv, bufsize=-1):
    """(argv : (string*), bufsize=-1) -> _ChildProcess
    
    Create a child process with pipes connected to its stdout, stdin and
    stderr file descriptors.  The child is created using fork() and
    execvp() in order to avoid the argument quoting problems presented by
    using system() or popen().  The bufsize argument has the same meaning as
    for the open() builtin and applies to stdin, stdout, and stderr.

    Examples:

        >>> p = execute(("ls", "/"))
        >>> p.readline()
        'bin\n'
        >>> p.readline()
        'boot\n'
        >>> p.close()
        >>>

        >>> p = execute(("cat",))
        >>> p.write("hello world\n")
        >>> p.stdin.close()
        >>> p.read()
        'hello world\n'
        >>> p.close()
        >>>

        >>> p = execute(("false",))
        >>> p.close()
        256
        >>>
    """
    return _ChildProcess(argv, bufsize)
