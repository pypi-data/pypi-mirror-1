from zope.interface import Interface
from zope.app.i18n import ZopeMessageFactory as _
from Acquisition import Explicit 

from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.Five import BrowserView


from plonehrm.notes.notes import Notes


class INotesViewlet(Interface):

    def getNotes():
        """return a list of notes"""
        
    def addNote(text):
        """add a note"""


class NoteAdd(BrowserView):

    def form_handle(self):
        """Create a new Note if the inline form is used.

        Only react if the form was submitted
        Only react if someone filled in text for the Note
        Make a new Note with the correct text
        Date will automatically be set to today
        """         
        response = self.request.response
        if self.request.has_key('notesform.submitted'):
            if self.request.has_key('titlesmallnote'):
                title = self.request['titlesmallnote']
                if title:
                    id = self.context.generateUniqueId('Note')
                    self.context.functioning.invokeFactory('Note', id=id)
                    newnote = self.context.functioning[id]
                    newnote.edit(title = title)
                    newnote._renameAfterCreation()
                    now = DateTime()
                    newnote.setDate(now)
                    message = "Note added"
        if message:
            url = (self.employeeUrl() +
                   '?portal_status_message=' + message)
            response.redirect(url)
        else:
            response.redirect(self.employeeUrl())


class NotesViewlet(Explicit):
    render = ViewPageTemplateFile('notes.pt')
    

    def __init__(self, context, request, view, manager):
        self.context = context
        self.request = request
        self.view = view
        self.manager = manager

    def getNotes(self):
        return self.context.get('notes', None)
        
        
    def addNote(self, text):
        notes = self.context.get('notes', None)
        if notes is None:
            self.notes = Notes()
        self.notes.addNote(text)

    def formAction(self):
        part1 = self.context.absolute_url()
        part2 = '/@@noteform/form_handle'
        return part1 + part2

    def canAddSmallnotes(self):
        """Return True if the user can add smallnotes.

        So, check the 'add content' permission.
        """

        mtool = getToolByName(self.context, 'portal_membership')
        checkPermission = mtool.checkPermission
        canAdd = checkPermission('Add portal content', self)
        return canAdd
