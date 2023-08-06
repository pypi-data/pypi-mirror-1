import logging
from zope.i18n import translate
from xml.sax.saxutils import escape

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

from zope.annotation.interfaces import IAnnotations
from persistent.list import PersistentList
from persistent.dict import PersistentDict

from plonehrm.checklist import config
from plonehrm.checklist import ChecklistMessageFactory as _
from checklist import CheckListItem

logger = logging.getLogger('plonehrm.checklist')

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

    ANNO_KEY = 'plonehrm.checklist'

    # tool-constructors have no id argument, the id is fixed
    def __init__(self, *args, **kwargs):
        self.setTitle(translate(_(u'title_portal_checklist',
                                  default=u'Checklist settings')))

    @property
    def items(self):
        annotations = IAnnotations(self)
        self.metadata = annotations.get(self.ANNO_KEY, None)
        if self.metadata is None:
            annotations[self.ANNO_KEY] = PersistentDict()
            self.metadata = annotations[self.ANNO_KEY]

        if not 'items' in self.metadata:
            self.metadata['items'] = PersistentList()

        return self.metadata['items']

    @property
    def next_id(self):
        """ The id for the next item.
        """
        annotations = IAnnotations(self)
        self.metadata = annotations.get(self.ANNO_KEY, None)
        if self.metadata is None:
            annotations[self.ANNO_KEY] = PersistentDict()
            self.metadata = annotations[self.ANNO_KEY]

        if not 'next_id' in self.metadata:
            if not self.items:
                next_id = 1
            else:
                # The next id will be the maximum id plus one.
                next_id = self.items[0].id
                for item in self.items:
                    if item.id > next_id:
                        next_id = item.id

                next_id += 1

            self.metadata['next_id'] = next_id

        return self.metadata['next_id']

    def _set_next_id(self, id):
        """ Explicitly set the id for the next item.
        """
        annotations = IAnnotations(self)
        self.metadata = annotations.get(self.ANNO_KEY, None)
        # The next line actually makes the next_id property available
        # if it is not there yet.
        current = self.next_id
        if current != id:
            self.metadata['next_id'] = id

    def _inc_next_id(self):
        """ Increments the next_id attribute.
        """
        annotations = IAnnotations(self)
        self.metadata = annotations.get(self.ANNO_KEY, None)
        if self.metadata is None:
            return

        if not 'next_id' in self.metadata:
            return

        self.metadata['next_id'] += 1


    security.declareProtected(ModifyPortalContent, 'indexObject')
    def indexObject(self):
        pass

    security.declareProtected(ModifyPortalContent, 'reindexObject')
    def reindexObject(self, idxs=[]):
        pass

    security.declareProtected(ModifyPortalContent, 'reindexObjectSecurity')
    def reindexObjectSecurity(self, skip_self=False):
        pass

    def _filterItems(self, objects, manager, is_end_contract=False):
        """ Filters objects stored in self.items.
        The objects parameter is a boolean, used to know
        if we return a list of CheckListItem objects or
        just their texts.
        The manager parameter is a boolean, used to know if
        we if we return manager items or not.
        """
        items = []
        for item in self.items:
            if item.isManager == manager and \
                   item.is_end_contract == is_end_contract:
                if objects:
                    items.append(item)
                else:
                    items.append(item.text)
        return items

    def _deleteItems(self, manager, is_end_contract=False):
        """ Deletes all items for which isManager equals manager.
        """
        items = self._filterItems(objects=True, manager=manager,
                                  is_end_contract=is_end_contract)
        for item in items:
            self.items.remove(item)

    def getDefaultItems(self, objects=False):
        """ Gets the list of non manager items.
        If object is set tot True, returns a list
        of CheckListItem. If objects is set to False,
        returns the list of items texts.
        """
        return tuple(self._filterItems(objects=objects, manager=False))

    def setDefaultItems(self, items):
        """ Takes a list of text and inserts it in
        self.items.
        """
        self._deleteItems(manager=False)
        for item in items:
            self.addItem(item)

    def getDefaultManagerItems(self, objects=False):
        """ Same than getDefaultItems but for manager items.
        """
        return tuple(self._filterItems(objects=objects, manager=True))

    def setDefaultManagerItems(self, items):
        """ Same than setDefaultItems, but create manager
        items.
        """
        self._deleteItems(manager=True)
        for item in items:
            self.addManagerItem(item)

    def addItem(self, item, addToAll=False, date=None,
                link_url=None, link_title=None):
        """Add an item to the default list.

        Optional: add it to all existing checklists.
        """
        return self._addItem(item, addToAll=addToAll, manager=False,
                             date=date, link_url=link_url,
                             link_title=link_title)

    def addManagerItem(self, item, addToAll=False, date=None,
                       link_url=None, link_title=None):
        """
        """
        return self._addItem(item, addToAll=addToAll, manager=True,
                             date=date, link_url=link_url,
                             link_title=link_title)

    def _existsItem(self, text):
        """ Returns a boolean telling if an item
        with the corresponding text exists in the list.
        """
        for item in self.items:
            if item.text == text:
                return True
        return False

    def _addItem(self, text, addToAll=False, manager=False, date=None,
                 link_url=None, link_title=None, is_end_contract=False):
        """ Adds an item in the checklist and returns it (or None
        it a previous item has the same name.)
        """
        # Strips html tags.
        stripped_text = escape(text)
        if self._existsItem(text):
            return

        item = CheckListItem(stripped_text,
                             date=date,
                             isManager=manager,
                             link_url=link_url,
                             link_title=link_title,
                             is_end_contract=is_end_contract)
        self.items.append(item)

        # We set the item's id.
        self.items[-1].id = self.next_id
        self._inc_next_id()

        if addToAll:
            catalog = getToolByName(self, 'portal_catalog')
            # Only search in parent, which might not be the root of
            # the site.
            parent = aq_parent(aq_inner(self))
            query = {'portal_type': 'Checklist',
                     'path': '/'.join(parent.getPhysicalPath())}
            brains = catalog(query)
            for brain in brains:
                try:
                    obj = brain.getObject()
                except (AttributeError, KeyError):
                    logger.warn("Error getting object at %s", brain.getURL())
                    continue

                if manager:
                    obj.addManagerItem(text, date=date,
                                       link_url=link_url,
                                       link_title=link_title)
                else:
                    obj.addItem(text, date=date,
                                link_url=link_url,
                                link_title=link_title)

        return item

    def editItem(self, id, text):
        """ Change the text of an item.
        The item is found by its id.

        Returns the item if the edit is a success.
        """
        if id is None or not text:
            return

        text = escape(text)
        # We check that an item with this text do not exist.
        for item in self.items:
            if item.text == text and not item.id == id:
                return

        for item in self.items:
            if item.id == id:
                # We update all items having the same texts in
                # employees checklist.
                catalog = getToolByName(self, 'portal_catalog')
                parent = aq_parent(aq_inner(self))
                query = {'portal_type': 'Checklist',
                         'path': '/'.join(parent.getPhysicalPath())}
                brains = catalog(query)
                for brain in brains:
                    try:
                        checklist = brain.getObject()
                    except (AttributeError, KeyError):
                        logger.warn("Error getting object at %s", brain.getURL())
                        continue

                    for employee_item in checklist.items:
                        # We check if the item's old text corresponds to any
                        # employee item text.
                        if employee_item.text == item.text:
                            employee_item.text = text
                    

                # We update the item text.
                item.text = text
                return item

    def deleteItem(self, id):
        """ Remove an item from the list.
        """
        if not id:
            return

        for item in self.items:
            if item.id == id:
                self.items.remove(item)
                continue

    def getEndContractItems(self):
        """ Gets all end contract items which are non-manager.
        """
        return tuple(self._filterItems(objects=True, manager=False,
                                       is_end_contract=True))

    def setEndContractItems(self, items):
        """ Sets all end contracts item
        """
        self._deleteItems(manager=False, is_end_contract=True)
        for item in items:
            self.addEndContractItem(item, is_end_contract=True)
    
    def addEndContractItem(self, text, date=None,
                link_url=None, link_title=None):
        """
        """
        return self._addItem(text, addToAll=False, manager=False,
                             date=date, link_url=link_url,
                             link_title=link_title,
                             is_end_contract=True)


registerType(ChecklistTool, config.PROJECTNAME)
