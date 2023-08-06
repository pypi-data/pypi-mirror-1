from kss.core import kssaction
from plone.app.kss.plonekssview import PloneKSSView
from Acquisition import Explicit
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import getSiteEncoding
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.interface import Interface

from plonehrm.notes.notes import Notes
from plonehrm.notes import NotesMessageFactory as _

MAXITEMS = 5


class INotesViewlet(Interface):

    def getNotes():
        """Return a list of (max 5) notes"""


class IAddNoteView(Interface):
    """Marker interface to add notes"""


def simple_add_note(context, text):
    if text is None or text =='':
        message = _(u'msg_no_input', default=u'No input provided')
    else:
        if context.get('notes', None) is None:
            context.notes = Notes()
        if not isinstance(text, unicode):
            text = unicode(text, getSiteEncoding(context))
        context.notes.addNote(text)
        message = _(u'msg_note_added', default=u'Note added')
    return message


def simple_remove_note(context, id):
    dummy = context.notes.pop(id)
    message = _(u'msg_note_removed', default=u'Note removed')
    return message


class AddNote(BrowserView):

    def __call__(self):
        """Create a new Note if the inline form is used.

        Only react if the form was submitted
        Only react if someone filled in text for the Note
        Make a new Note with the correct text
        Date will automatically be set to today
        """
        text = self.request.get('text', None)
        message = simple_add_note(self.context, text)
        self.context.plone_utils.addPortalMessage(message)
        response = self.request.response
        here_url = self.context.absolute_url()
        response.redirect(here_url)


class NotesViewlet(Explicit):
    """A viewlet for seeing and adding notes."""

    template = ViewPageTemplateFile('notes.pt')

    def __init__(self, context, request, view=None, manager=None):
        self.context = context
        self.request = request
        self.view = view
        self.manager = manager
        membership = getToolByName(self.context, 'portal_membership')
        self.checkPermission = membership.checkPermission
        # TODO: ^^^ not used
        self.encoding = getSiteEncoding(context)

    def getNotes(self):
        notes = self.context.get('notes', None)
        if notes is None:
            return None
        notes = notes[-MAXITEMS:]
        notes.reverse()
        return notes

    def render(self):
        # The zope3 viewlet manager expects that render() will return
        # unicode objects ... but by default zope 2.9's zpt engine returns
        # str objects.  With Zope 2.10, zpt's should return unicodes which
        # would make this work ok.
        val = self.template()
        if not isinstance(val, unicode):
            val = unicode(val, self.encoding)
        return val


class NoteAddView(PloneKSSView):
    """kss view for adding a note"""
    @kssaction
    def add_note(self, text):
        """Add a note"""
        core = self.getCommandSet('core')
        selector = core.getHtmlIdSelector('notes')
        message = simple_add_note(self.context, text)
        view = self.context.restrictedTraverse('@@plonehrm.notes')
        rendered = view.render()
        core.replaceHTML(selector, rendered)
        # Set the focus on the input field, which also clears the
        # previous text entered.
        core.focus('#new-note')


class NoteRemoveView(PloneKSSView):
    """kss view for removing a note"""
    @kssaction
    def remove_note(self, id):
        """Remove a note by id

        Warning: the following situation might occur:
        1. Harry loads the page of an Employee and sees note A.
        2. Sally does the same and adds a new note B.
        3. Harry clicks to remove note A (the top one for him).
        4. Note B (which is the real top one) gets removed instead.

        If this bytes you, feel free to fix it. :)
        """
        core = self.getCommandSet('core')
        # 'remove-1' should become -1
        id = int(id[len('remove'):])
        simple_remove_note(self.context, id)
        view = self.context.restrictedTraverse('@@plonehrm.notes')
        rendered = view.render()
        selector = core.getHtmlIdSelector('notes')
        core.replaceHTML(selector, rendered)
        # Set the focus on the input field, which also clears the
        # previous text entered.
        core.focus('#new-note')
