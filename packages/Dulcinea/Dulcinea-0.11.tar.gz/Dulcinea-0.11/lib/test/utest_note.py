"""
$URL: svn+ssh://svn.mems-exchange.org/repos/trunk/dulcinea/lib/test/utest_note.py $
$Id: utest_note.py 27147 2005-08-03 13:59:08Z dbinger $
"""
from dulcinea.note import Note, Notable
from sancho.utest import UTest

class TestNotable(Notable):
    pass

class Test (UTest):

    def _pre(self):
        self.note = Note()
        self.notable = TestNotable()

    def check_note(self):
        assert self.note.get_text() is None
        self.note.set_text('foo')
        assert self.note.get_text() == 'foo'
        assert Note('bar').get_text() == 'bar'

    def check_notable(self):
        assert self.notable.get_note() is None
        self.notable.set_note(self.note)
        assert self.notable.get_note() is self.note
        assert TestNotable(Note('foo')).get_note().get_text() == 'foo'

if __name__ == "__main__":
    Test()
