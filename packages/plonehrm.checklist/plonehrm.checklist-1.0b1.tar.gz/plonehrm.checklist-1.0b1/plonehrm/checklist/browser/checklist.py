from Acquisition import Explicit
from Acquisition import aq_inner
from Products.CMFCore.utils import getToolByName
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.interface import implements
from zope.viewlet.interfaces import IViewlet

from plonehrm.checklist import ChecklistMessageFactory as _


class ChecklistToolView(BrowserView):
    """View for dealing with the checklist tool."""

    def form_action(self):
        """
        """
        part1 = self.context.absolute_url()
        part2 = '/@@checklisttool_view/form_handle'
        return part1 + part2

    def form_handle(self):
        """
        """
        response = self.request.response
        clt = getToolByName(self.context, 'portal_checklist')
        if not self.request.has_key('checklistform.submitted'):
            return response.redirect(self.employeeUrl())

        if self.request.has_key('checklistform.config_normal'):
            if (not self.request.has_key('item_add') or
                not self.request['item_add']):

                return response.redirect(clt.absolute_url())
            addToAll = (self.request.has_key('apply_to_all') and
                        self.request['apply_to_all'])
            clt.addItem(self.request['item_add'], addToAll)
            return response.redirect(clt.absolute_url())

        if self.request.has_key('checklistform.config_manager'):
            if (not self.request.has_key('manager_item_add') or
                not self.request['manager_item_add']):
                return response.redirect(clt.absolute_url())
            addToAll = (self.request.has_key('apply_to_all') and
                        self.request['apply_to_all'])
            clt.addManagerItem(self.request['manager_item_add'],addToAll)
            return response.redirect(clt.absolute_url())


    def employeeUrl(self):
        """Return the URL of the parent (=employee).
        """

        return self.context.absolute_url()

    def _uniqueTuple(self, mylist):
        """Return a tuple with unique items (kick out duplicates)
        """
        items = list(set(mylist))
        return tuple(items)


class UpdateChecklist(BrowserView):
    """For updating a checklist."""

    def __call__(self):
        """Update the checklist.

        Only react if the form was submitted
        Only react if someone filled in text for the Note
        Make a new Note with the correct text
        Date will automatically be set to today
        """
        response = self.request.response
        context = aq_inner(self.context)
        clt = getToolByName(context, 'portal_checklist')
        msg = None

        scratch = dict(self.request)
        hrmmgritems = []
        for key in scratch.keys():
            if key.startswith('hrmmgr'):
                del scratch[key]
                hrmmgritems.append(key[6:])

        hrmitems = []
        for key in scratch.keys():
            if key.startswith('hrm'):
                del scratch[key]
                hrmitems.append(key[3:])

        checklist = context.checklist

        plone_utils = getToolByName(context, 'plone_utils')
        if hrmmgritems:
            checkeditems = list(checklist.getCheckedManagerItems())
            newitems = tuple(list(set(hrmmgritems + checkeditems)))
            checklist.setCheckedManagerItems(newitems)
            message = _(u'msg_manger_items_updated',
                        default=u'Manager checklist items updated')
            plone_utils.addPortalMessage(message)
        if hrmitems:
            # check if normal items were submitted
            checkeditems = list(checklist.getCheckedItems())
            newitems =  tuple(list(set(hrmitems + checkeditems)))
            checklist.setCheckedItems(newitems)
            message = _(u'msg_items_updated', default=u'Checklist items updated')
            plone_utils.addPortalMessage(message)
        # And now back to where we came from.
        response.redirect(context.absolute_url())


class ChecklistView(Explicit):
    """Viewlet for seeing a checklist."""

    implements(IViewlet)
    render = ViewPageTemplateFile('checklist.pt')

    def __init__(self, context, request, view=None, manager=None):
        self.__parent__ = view
        self.context = context
        self.request = request
        self.view = view
        self.manager = manager

    def update(self):
        self.checklist = self.context.checklist

    def canEditItems(self):
        """Return if we can edit the items.
        """
        mtool = getToolByName(self.context, 'portal_membership')
        return mtool.checkPermission('plonehrm: Modify checklist',
                                     self.context)

    def canEditManagerItems(self):
        """Return if we can edit the manager items.
        """
        mtool = getToolByName(self.context, 'portal_membership')
        return mtool.checkPermission('plonehrm: Modify manager checklist',
                                     self.context)

    def items_left(self):
        """
        """
        return len(self.checklist.remainingItems()) > 0

    def manager_items_left(self):
        """
        """
        return len(self.checklist.remainingManagerItems()) > 0

    def any_items_left(self):
        """
        """
        return self.items_left() or self.manager_items_left()


class SimpleChecklistView(ChecklistView):
    """Simple viewlet for seeing a checklist."""
    implements(IViewlet)
    render = ViewPageTemplateFile('simple_checklist.pt')

    def header(self):
        return 'Checklist'
