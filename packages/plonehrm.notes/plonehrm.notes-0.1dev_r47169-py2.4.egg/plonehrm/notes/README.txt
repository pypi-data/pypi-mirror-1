Notes
=====

This extension module add very simple note to plonehrm's employee type.

Overview
--------

A plonehrm extension module to add note to an employee.

>>> from plonehrm.notes.notes import Note, Notes


A Note is persistent dict with a simple unicode string and a date 

>>> n1 = Note(u'My first little note.')
>>> n1.text
u'My first little note.'


>>> from datetime import date
>>> n1.date == date.today().isoformat()
True

Notes is a persistent list that stores the notes.

>>> nts = Notes()

But it only takes text as input, not an already existing note:

>>> nts.addNote(n1)
Traceback (most recent call last):
AssertionError: string expected, got <class 'plonehrm.notes.notes.Note'>

We can still add the plain text of a Note though.

>>> nts.addNote(n1.text)
>>> nts.addNote(u'It could be much longer if you prefer that.')
>>> print nts
[<plonehrm.notes.notes.Note object at ...>, <plonehrm.notes.notes.Note object at ...>]


>>> n3 = Note(u"Hé daar!")
>>> unicode(n3.text)
u'H\xc3\xa9 daar!'
>>> n3.text
u'H\xc3\xa9 daar!'

