from zope.i18n import translate

from Products.Archetypes.atapi import BaseContent
from Products.Archetypes.atapi import BaseSchema
from Products.Archetypes.atapi import LinesField
from Products.Archetypes.atapi import Schema
from Products.Archetypes.atapi import registerType
from Products.CMFCore.utils import UniqueObject
from Products.CMFCore.utils import getToolByName

from plonehrm.checklist import config
from plonehrm.checklist import ChecklistMessageFactory as _

schema = Schema((
    LinesField(
        name='defaultItems',
        widget=LinesField._properties['widget'](
            label=_(u'label_defaultItems', default=u'Default items'),
        ),
    ),
    LinesField(
        name='defaultManagerItems',
        widget=LinesField._properties['widget'](
            label=_(u'label_defaultManagerItems',
                    default=u'Default items (for the HRM manager)'),
        ),
    ),
),
)

ChecklistTool_schema = BaseSchema.copy() + schema.copy()


class ChecklistTool(UniqueObject, BaseContent):
    """
    """
    __implements__ = (BaseContent.__implements__,)

    id = 'portal_checklist'
    typeDescription = _(u'description_portal_checklist',
                        default=u'Checklist settings')
    schema = ChecklistTool_schema

    # tool-constructors have no id argument, the id is fixed
    def __init__(self):
        self.id = 'portal_checklist'
        self.setTitle(translate(_(u'title_portal_checklist',
                                  default=u'Checklist settings')))
        self.unindexObject()

    # tool should not appear in portal_catalog
    def at_post_edit_script(self):
        self.unindexObject()

    def addItem(self, item, addToAll=False):
        """Add an item to the default list.

        Optional: add it to all existing checklists.
        """
        return self._addItem(item, addToAll, False)

    def addManagerItem(self, item, addToAll=False):
        """
        """
        return self._addItem(item, addToAll, True)

    def _addItem(self, item, addToAll=False, manager=False):
        """
        """
        if manager:
            default = self.getDefaultManagerItems()
        else:
            default = self.getDefaultItems()
        if item in default:
            # We're not adding it a second time.
            return
        default = list(default) # Making sure it is no tuple...
        default.append(item)
        if manager:
            self.setDefaultManagerItems(default)
        else:
            self.setDefaultItems(default)
        if addToAll:
            catalog = getToolByName(self, 'portal_catalog')
            query = {'portal_type': 'Checklist'}
            brains = catalog(query)
            for brain in brains:
                obj = brain.getObject()
                if manager:
                    obj.addManagerItem(item)
                else:
                    obj.addItem(item)

registerType(ChecklistTool, config.PROJECTNAME)
