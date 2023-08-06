from xml.sax.saxutils import unescape

from Acquisition import Explicit
from Acquisition import aq_inner
from Products.CMFCore.utils import getToolByName
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.interface import implements
from zope.viewlet.interfaces import IViewlet
from zope.i18n import translate

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


    def get_content(self):
        view = self.context.restrictedTraverse('@@checklisttool_edit')
        return view.index()

class ChecklistToolEdit(BrowserView):
    """ Displays the form used to edit default checklist items.
    """
    
    def get_sorted_items(self):
        """ Provides a dictionnary used to simplify templates
        to manage the items.
        
        This dictionnary looks like this:

        {'default': [list of default items, 'Default items',
                     '', True],
         'manager': [list of manager items, 'Default manager items',
                     '', True],
         'endcontract': [list of end contract items, 'End contract items',
                          '', False],
        }

        The second item of the list is translated according to the
        user language, the third one is a potential help message and
        the last one is used to know if new items can be added to
        all users.
        """

        result = {}
        props = getToolByName(self.context, 'portal_properties')
        lang = props.site_properties.getProperty('default_language')

        descDefault = _(u'desc_default_items',
                        u'Those tasks are automatically added when you' + \
                        ' add an employee to the system.')
        result['default'] = [self.context.getDefaultItems(objects=True),
                             translate(_(u'default-items',
                                         u'Employment start tasks'),
                                       target_language=lang),
                             translate(descDefault, target_language=lang),
                             True]

        descManager = _(u'desc_manager_items',
                        u'Same than default tasks, but can be added by a' + \
                        ' worklocation manager.')

        result['manager'] = [self.context.getDefaultManagerItems(objects=True),
                             translate(_(u'default-manager-items',
                                         u'Employment start manager tasks'),
                                       target_language=lang),
                             translate(descManager, target_language=lang),
                             True]

        descEnd = _(u'desc_end_items',
                    u'Those tasks are added when an employee leaves' + \
                    ' the company.')

        result['endcontract'] = [self.context.getEndContractItems(),
                                  translate(_(u'end-contract-items',
                                              u'Employment termination items'),
                                       target_language=lang),
                             translate(descEnd, target_language=lang),
                                 False]

        return result


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
            checklist.setCheckedManagerItems(hrmmgritems)
            message = _(u'msg_manger_items_updated',
                        default=u'Manager checklist items updated')
            plone_utils.addPortalMessage(message)
        if hrmitems:
            # check if normal items were submitted
            checklist.setCheckedItems(hrmitems)
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

        self.checklist = self.context.checklist

        # This attribute is used to know if we display the list
        # of tasks or the form to add/edit a task.
        # Possible values are: list, form_new, form_edit.
        self.view_mode = "list"

        self.editedItem = None

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
        return len(self.checklist.getAllItems()) > 0

    def manager_items_left(self):
        """
        """
        return len(self.checklist.getAllManagerItems()) > 0

    def any_items_left(self):
        """
        """
        return self.items_left() or self.manager_items_left()

    def unescape_text(self, text):
        """ Unescape specials html character from the text.
        For example, &gt; will return >.
        """
        if text:
            return unescape(text)

class SimpleChecklistView(ChecklistView):
    """Simple viewlet for seeing a checklist."""
    implements(IViewlet)
    render = ViewPageTemplateFile('simple_checklist.pt')

    def header(self):
        return 'Checklist'
