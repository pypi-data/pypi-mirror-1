__author__ = """unknown <unknown>"""
__docformat__ = 'plaintext'

from AccessControl import ClassSecurityInfo
from zope import interface
from Products.Archetypes.atapi import Schema
from Products.Archetypes.atapi import LinesField
from Products.Archetypes.atapi import MultiSelectionWidget
from Products.Archetypes.atapi import BaseFolderSchema
from Products.Archetypes.atapi import BaseFolder
from Products.Archetypes.atapi import registerType
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import getSiteEncoding
from Products.plonehrm.interfaces import IEmployeeModule
from plonehrm.checklist import config
from plonehrm.checklist import ChecklistMessageFactory as _
from plonehrm.checklist.interfaces import IChecklist

schema = Schema((

    LinesField(
        name='checkedItems',
        read_permission='plonehrm: View hrm content',
        write_permission='plonehrm: Modify checklist',
        widget=MultiSelectionWidget(
            size=8,
            format="checkbox",
            label=_(u'label_checkedItems',
                    default=u'Already checked items'),
        ),
        vocabulary='getAllItems',
    ),
    LinesField(
        name='allItems',
        read_permission='plonehrm: View hrm content',
        write_permission='plonehrm: Modify checklist',
        widget=LinesField._properties['widget'](
            visible=0,
            label=_(u'label_allItems',
                    default=u'All items that ought to be checked'),
        ),
    ),
    LinesField(
        name='checkedManagerItems',
        read_permission='plonehrm: View hrm content',
        write_permission='plonehrm: Modify manager checklist',
        vocabulary='getAllManagerItems',
        widget=MultiSelectionWidget(
            format="checkbox",
            size=8,
            label=_(u'label_checkedManagerItems',
                    default=u'Already checked manager items'),
        ),
    ),
    LinesField(
        name='allManagerItems',
        read_permission='plonehrm: View hrm content',
        write_permission='plonehrm: Modify manager checklist',
        widget=LinesField._properties['widget'](
            visible=0,
            label=_(u'label_allManagerItems',
                   default=u'All manager items that ought to be checked'),
        ),
    ),
),
)

Checklist_schema = BaseFolderSchema.copy() + schema.copy()
Checklist_schema['title'].widget.visible = 0
Checklist_schema['description'].widget.visible = 0


def checkArgs(argname, **kwargs):
    """ Simple method used to factorize code from the findItem.
    Returns True if argname exists in kwargs and if the value is
    True.

    >>> checkArgs('test')
    False

    >>> checkArgs('test', p1 = 42)
    False

    >>> checkArgs('test', p1 = 42, test = True)
    True

    >>> checkArgs('test', p1 = 42, test = False)
    False
    """
    return (argname in kwargs) and kwargs[argname] == True


class Checklist(BaseFolder):
    """
    """
    __implements__ = (getattr(BaseFolder, '__implements__', ()), )
    interface.implements(IEmployeeModule, IChecklist)

    typeDescription = "Checklist"
    typeDescMsgId = 'description_edit_checklist'
    _at_rename_after_creation = True
    schema = Checklist_schema

    def remainingItems(self):
        """Return the items that have not yet been checked.
        """
        all = self.getAllItems()
        alreadyChecked = self.getCheckedItems()
        remaining = [item for item in all
                     if not item in alreadyChecked]
        return tuple(remaining)

    def addItem(self, item):
        """Add an item to the list of to-check items.
        """

        all = self.getAllItems()
        if item in all:
            # We're not adding it a second time.
            return
        all = list(all) # Making sure it is no tuple...
        all.append(item)
        self.setAllItems(all)

    def remainingManagerItems(self):
        """Return the manager items that have not yet been checked.
        """
        all = self.getAllManagerItems()
        alreadyChecked = self.getCheckedManagerItems()
        remaining = [item for item in all
                     if not item in alreadyChecked]
        return tuple(remaining)

    def addManagerItem(self, item):
        """Add an item to the list of manager to-check items.
        """
        all = self.getAllManagerItems()
        encoding = getSiteEncoding(self)
        if not isinstance(item, unicode):
            item = unicode(item, encoding)
        all = [unicode(i, encoding) for i in all]
        if item in all:
            # We're not adding it a second time.
            return
        all = list(all) # Making sure it is no tuple...
        all.append(item)
        self.setAllManagerItems(all)

    def initializeArchetype(self, **kwargs):
        """Pre-populate the checklist.
        """

        BaseFolder.initializeArchetype(self, **kwargs)
        ct = getToolByName(self, 'portal_checklist')
        self.setAllItems(ct.getDefaultItems())
        self.setAllManagerItems(ct.getDefaultManagerItems())

    def findItems(self, pattern, **kwargs):
        """ Search in the item list. Pattern is the string that is
        searched in the items.
        A few keys are recognized in kwargs:
        - startswith: if set to True, search only items beginning with
          the pattern
        - endswith: if set to True, search only items ending with the
          pattern
        - checked: if set to True, only seeks for checked items
        - unchecked: if set to True, only seeks for unchecked items

        Returns the list of items corresponding to the search.
        """

        starts_with = checkArgs('startswith', **kwargs)
        ends_with = checkArgs('endswith', **kwargs)
        checked = checkArgs('checked', **kwargs)
        unchecked = checkArgs('unchecked', **kwargs)

        # In this case, nothing can be returned.
        if checked and unchecked:
            return tuple([])

        # Only checked items are searched.
        if checked:
            items = self.getCheckedItems()

        # Only remaining items are searched.
        if unchecked:
            items = self.remainingItems()

        # Every items are searched.
        if not checked and not unchecked:
            items = self.getAllItems()

        results = []

        for item in items:
            # Checks if the pattern exists in the item
            added = not (item.find(pattern) == -1)

            if added and starts_with:
                added = item.startswith(pattern)

            if added and ends_with:
                added = item.endswith(pattern)

            if added:
                results.append(item)

        return tuple(results)

    def deleteItem(self, item):
        """ Delete an item from the list.

        XXX Currently this is only done for the normal (non-Manager)
        items.
        """
        # Delete the item from the allItems field.
        all = list(self.getAllItems())
        if item in all:
            all.remove(item)
            self.setAllItems(all)

        # Delete the item from the checkedItems field.
        all = list(self.getCheckedItems())
        if item in all:
            all.remove(item)
            self.setCheckedItems(all)


registerType(Checklist, config.PROJECTNAME)
