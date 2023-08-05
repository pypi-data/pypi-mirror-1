"""
$Id: note.py 27538 2005-10-11 23:00:36Z rmasse $
$URL: svn+ssh://svn.mems-exchange.org/repos/trunk/dulcinea/lib/note.py $
"""

from dulcinea.attachable import Attachable
from dulcinea.base import DulcineaPersistent
from dulcinea.spec import specify, string

class Note(DulcineaPersistent, Attachable):

    text_is = (string, None)

    def __init__(self, text=None):
        Attachable.__init__(self)
        self.set_text(text)

    def get_text(self):
        return self.text

    def set_text(self, text):
        specify(self, text=text)

    def is_empty(self):
        return not bool(self.text or self.get_attachments())

class Notable:

    note_is = (Note, None)

    def __init__(self, note=None):
        self.set_note(note)

    def set_note(self, note):
        specify(self, note=note)

    def get_note(self):
        return self.note
