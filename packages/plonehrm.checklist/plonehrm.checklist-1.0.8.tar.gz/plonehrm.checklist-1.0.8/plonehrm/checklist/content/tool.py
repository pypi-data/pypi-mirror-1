from zope.i18n import translate

from AccessControl import ClassSecurityInfo
from Acquisition import aq_inner, aq_parent
from Products.Archetypes.atapi import BaseContent
from Products.Archetypes.atapi import BaseSchema
from Products.Archetypes.atapi import LinesField
from Products.Archetypes.atapi import Schema
from Products.Archetypes.atapi import registerType
from Products.CMFCore.utils import ImmutableId
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.permissions import ModifyPortalContent

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


class ChecklistTool(ImmutableId, BaseContent):
    """Checklist Tool.
    """
    security = ClassSecurityInfo()
    __implements__ = (BaseContent.__implements__, )

    id = 'portal_checklist'
    typeDescription = _(u'description_portal_checklist',
                        default=u'Checklist settings')
    schema = ChecklistTool_schema

    # tool-constructors have no id argument, the id is fixed
    def __init__(self, *args, **kwargs):
        self.setTitle(translate(_(u'title_portal_checklist',
                                  default=u'Checklist settings')))

    security.declareProtected(ModifyPortalContent, 'indexObject')
    def indexObject(self):
        pass

    security.declareProtected(ModifyPortalContent, 'reindexObject')
    def reindexObject(self, idxs=[]):
        pass

    security.declareProtected(ModifyPortalContent, 'reindexObjectSecurity')
    def reindexObjectSecurity(self, skip_self=False):
        pass

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
            # Only search in parent, which might not be the root of
            # the site.
            parent = aq_parent(aq_inner(self))
            query = {'portal_type': 'Checklist',
                     'path': '/'.join(parent.getPhysicalPath())}
            brains = catalog(query)
            for brain in brains:
                obj = brain.getObject()
                if manager:
                    obj.addManagerItem(item)
                else:
                    obj.addItem(item)

registerType(ChecklistTool, config.PROJECTNAME)
