"""
$URL: svn+ssh://svn.mems-exchange.org/repos/trunk/dulcinea/lib/test/utest_child_process.py $
$Id: utest_child_process.py 27147 2005-08-03 13:59:08Z dbinger $
"""
from dulcinea import child_process
from sancho.utest import UTest

class ChildProcessTest (UTest):

    def check_cat (self):
        p = child_process.execute(('cat',))
        p.write("hello world\n")
        p.stdin.close()
        line = p.readline()
        assert line == 'hello world\n', repr(line)
        assert p.close() == None

    def check_ls (self):
        p = child_process.execute(("ls", "/"))
        assert "bin" in p.read()
        assert p.close() == None

    def check_error (self):
        p = child_process.execute(("false",))
        assert p.close() == 256


if __name__ == "__main__":
    ChildProcessTest()
