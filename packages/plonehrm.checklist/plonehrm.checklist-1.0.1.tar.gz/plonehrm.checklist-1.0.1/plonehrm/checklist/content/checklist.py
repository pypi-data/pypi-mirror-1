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


class Checklist(BaseFolder):
    """
    """
    __implements__ = (getattr(BaseFolder,'__implements__',()),)
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

        BaseFolder.initializeArchetype(self,**kwargs)
        ct = getToolByName(self, 'portal_checklist')
        self.setAllItems(ct.getDefaultItems())
        self.setAllManagerItems(ct.getDefaultManagerItems())


registerType(Checklist, config.PROJECTNAME)
