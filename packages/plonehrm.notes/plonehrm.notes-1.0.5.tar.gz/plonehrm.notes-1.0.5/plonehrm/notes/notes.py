from datetime import date

from interfaces import INote
from interfaces import INotes
from persistent.dict import PersistentDict
from persistent.list import PersistentList
from zope.interface import implements


class Notes(PersistentList):
    implements(INotes)

    def addNote(self, text):
        assert(isinstance(text, basestring)), \
            "string expected, got %s" % type(text)
        self.append(Note(text))

    def removeNote(self, text):
        assert(isinstance(text, basestring)), \
            "string expected, got %s" % type(text)
        self.remove(Note(text))


class Note(PersistentDict):
    implements(INote)
    def __init__(self, text):
        super(Note, self).__init__()
        self['text'] = text
        self['date'] = date.today()

    @property
    def text(self):
        return self['text']

    @property
    def date(self):
        return self['date'].isoformat()
