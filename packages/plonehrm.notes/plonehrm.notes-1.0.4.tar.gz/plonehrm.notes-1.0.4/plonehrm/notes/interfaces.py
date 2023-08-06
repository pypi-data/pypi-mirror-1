from zope.schema import List, TextLine, Date
from zope.interface import Interface
from zope.i18n import MessageFactory
from datetime import date

_ = MessageFactory('notesmodules')


class INotes(Interface):

    notes = List(title=_(u'A list of notes'),
                 required=False,
                 default=[])


class INote(Interface):

    text = TextLine(title=_(u'Note'),
                       required=True,
                       default=u"",)

    date = Date(title=_(u'Date'),
                required=True,
                default=date.today())
