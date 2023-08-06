__author__ = """unknown <unknown>"""
__docformat__ = 'plaintext'

import logging
from xml.sax.saxutils import escape

from zope import interface
from AccessControl import Unauthorized
from Products.Archetypes.atapi import Schema
from Products.Archetypes.atapi import LinesField
from Products.Archetypes.atapi import MultiSelectionWidget
from Products.Archetypes.atapi import BaseFolderSchema
from Products.Archetypes.atapi import BaseFolder
from Products.Archetypes.atapi import registerType
from Products.CMFCore.utils import getToolByName
from Products.plonehrm.interfaces import IEmployeeModule
from plonehrm.checklist import config
from plonehrm.checklist import ChecklistMessageFactory as _
from plonehrm.checklist.interfaces import IChecklist
from zope.annotation.interfaces import IAnnotations
from persistent.list import PersistentList
from persistent.dict import PersistentDict
from persistent import Persistent

logger = logging.getLogger('maurits.refactoring')

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


class CheckListItem(Persistent):
    """ This class describes an item of the CheckList.

    >>> item = CheckListItem('No link')
    >>> item.is_link
    False
    >>> item.link_url="http://www.test.com"
    >>> item.is_link
    True
    """

    def __init__(self,
                 text,
                 date = None,
                 isManager = False,
                 link_url=None,
                 link_title=None,
                 id=0,
                 is_end_contract=False,
                 notification=False,
                 email=None):
        self.text = text
        self.date = date
        self.isManager = isManager
        self.link_url = link_url
        self.link_title = link_title
        self.is_end_contract = is_end_contract
        self.id = id
        self.notification = notification
        self.email = email

    @property
    def is_link(self):
        """ Checks is the link_url property is set.
        """
        return bool(self.link_url)

    def get_style(self):
        """ This method is used to set a style when displaying
        items.
        If the item's date is in the past, then it returns 'past'
        If the item's date is today, it returns 'today'
        In other cases, it returns 'normal'
        """
        if self.date:
            if self.date.isCurrentDay():
                return 'today'
            elif self.date.isPast():
                return 'past'
            else:
                return 'normal'
        else:
            return 'normal'


class Checklist(BaseFolder):
    """ This class used to be a real Archetype.
    We refactored it to use Annotations and PersistentLists, but kept
    the original methods to avoid side effects.

    The list of items is now stored in self.items and each item
    has for type CheckListItem.
    """
    __implements__ = (getattr(BaseFolder, '__implements__', ()), )
    interface.implements(IEmployeeModule, IChecklist)

    typeDescription = "Checklist"
    typeDescMsgId = 'description_edit_checklist'
    _at_rename_after_creation = True
    schema = Checklist_schema

    ANNO_KEY = 'plonehrm.checklist'

    def __init__(self, *args, **kwargs):
        BaseFolder.__init__(self, *args, **kwargs)

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

    def _filterItems(self, objects=False, **kwargs):
        """ Filter items depending on some criteria in kwargs:

        - isManager: if set, only returns manager items or all items.

        The object item is used to know if the method returns a list of
        CheckListItem() objects or just the list of their texts.
        """
        items = []

        if 'isManager' in kwargs:
            manager_filter = True
            manager = kwargs['isManager']
        else:
            manager_filter = False
            manager = False

        for item in self.items:
            append = True

            # If the manager filter is set and the
            # item does not correspond to the filter, we
            # do not append the item.
            if manager_filter and \
               not item.isManager == manager:
                append = False

            if append:
                if objects:
                    items.append(item)
                else:
                    items.append(item.text)

        return items

    def _deleteItems(self,
                     **kwargs):
        """ Delete items in the list (used to clean list
        in the set[...]Items() methods.)
        The kwargs are the same as those used by _filterItems.
        """
        items = self._filterItems(objects=True, **kwargs)

        for item in items:
            self.items.remove(item)

    def getAllItems(self, objects=False):
        """ Fetches all items in the checklist.
        If objects is set to True, then it returns a list of
        objects, if None, it returns the texts of the items.

        This only fetches non manager items.
        """
        return tuple(self._filterItems(objects, isManager=False))

    def setAllItems(self, items):
        """ Takes a list of texts and insert one item for each one.

        Only sets non manager items.
        """
        self._deleteItems(isManager=False)
        for item in items:
            self.addItem(item)

    def getAllManagerItems(self, objects=False):
        """ Fetches all manager items in the checklist.
        """
        return tuple(self._filterItems(objects, isManager = True))

    def setAllManagerItems(self, items):
        """ Same as setAlItems(), but adds manager items.
        """
        self._deleteItems(isManager=True)
        for item in items:
            self.addManagerItem(item)

    def getCheckedItems(self, objects=False):
        """ Same principle as the getAllItems() method,
        except that it only fetches items for which
        the 'checked' property is set to True.
        """
        logger.warn('getCheckedItems needlessly called')
        return []

    def setCheckedItems(self, items):
        """ Same principle as setAllItems, but creates checked items.

        Note that items are only strings.
        """
        for item in items:
            item_to_remove = self.findItem(text=item)
            if item_to_remove:
                self.items.remove(item_to_remove)

    def getCheckedManagerItems(self, objects=False):
        """ Same principle as the getCheckedItems() method,
        except that it filters only manager items.
        """
        logger.warn('getCheckedManagerItems needlessly called')
        return []

    def setCheckedManagerItems(self, items):
        """ Same principle as setAllmanagerItems, but creates checked
        items.
        """
        self.setCheckedItems(items)

    def remainingItems(self, objects=False):
        """ Works the same way as the getCheckedItems(),
        except that it returns items that have not been checked.
        """
        logger.warn('remainingItems -> getAllItems')
        return self.getAllItems(objects=objects)

    def remainingManagerItems(self, objects=False):
        """ Same as remainingItems() but for manager items.
        """
        logger.warn('remainingItems -> getAllItems')
        return self.getAllManagerItems(objects=objects)

    def remainingAllItems(self):
        """ Returns all remaining items (manager and not manager.)
        It first displays non manager items, then manager items.
        """
        items = list(self.getAllItems(objects=True))
        items.extend(list(self.getAllManagerItems(objects=True)))
        return items

    def _addItem(self,
                 text,
                 date=None,
                 isManager=False,
                 link_url=None,
                 link_title=None,
                 notification=False,
                 email=None):
        """ Adds a new item to the list. This method
        shall not be called directly. Items should be added
        with addItem() or addManagerItem().
        """
        # Strips html tags.
        text = escape(text)

        item = CheckListItem(text, date, isManager,
                             link_url, link_title,
                             notification=notification,
                             email=email)
        self.items.append(item)

        # We set the item's id.
        self.items[-1].id = self.next_id
        self._inc_next_id()

    def findItem(self, text=None, id=None):
        """ Returns the first item which text corresponds
        to the 'text' parameter of the id.
        """
        for item in self.items:
            if item.text == text or item.id == id:
                return item
        return None

    def _existsItem(self, text):
        """ Checks if an item with this text exists in
        the list.
        """
        return bool(self.findItem(text=text))

    def addItem(self, text, date=None,
                link_url=None, link_title=None, allow_double=True,
                notification=False, email=None):
        """Add an item to the list of to-check items.

        If allow_double is False, we only add the item if no item with
        that text already exists.  So: *only the text* is checked.
        """
        if allow_double or not self._existsItem(text):
            self._addItem(text, date=date, link_url=link_url,
                          link_title=link_title,
                          notification=notification, email=email)

    def addManagerItem(self, text, date=None,
                       link_url=None, link_title=None, allow_double=True,
                       notification=False, email=None):
        """Add an item to the list of manager to-check items.

        If allow_double is False, we only add the item if no item with
        that text already exists.  So: *only the text* is checked.
        """
        if allow_double or not self._existsItem(text):
            self._addItem(text, isManager=True,
                          date=date, link_url=link_url,
                          link_title=link_title,
                          notification=notification, email=email)

    def checkItem(self, id=None, text=None):
        """ Checks an item, found by its id or name.

        Checking has changed to just mean: deleting.
        """
        for item in self.items:
            if item.id == id or item.text == text:
                mtool = getToolByName(self, 'portal_membership')
                if item.isManager:
                    if not mtool.checkPermission(
                        'plonehrm: Modify manager checklist',
                        self):
                        raise Unauthorized
                else:
                    if not mtool.checkPermission(
                        'plonehrm: Modify checklist',
                        self):
                        raise Unauthorized
                self.items.remove(item)
                return

    def editItem(self, id, text, date=None,
                 link_url=None, link_title=None,
                 notification=True, email=None):
        """ Edit properties of an item.
        """
        for item in self.items:
            if item.id == id:
                mtool = getToolByName(self, 'portal_membership')
                if item.isManager:
                    if not mtool.checkPermission(
                        'plonehrm: Modify manager checklist',
                        self):
                        raise Unauthorized
                else:
                    if not mtool.checkPermission(
                        'plonehrm: Modify checklist',
                        self):
                        raise Unauthorized
                item.text = escape(text)
                item.date = date
                item.notification = notification
                item.email = email

                if link_url:
                    item.link_url = link_url
                if link_title:
                    item.link_title = link_title
                return

    def deleteItem(self, text):
        """ Removes an item from the list.
        """
        item = self.findItem(text=text)
        if item:
            mtool = getToolByName(self, 'portal_membership')
            if item.isManager:
                if not mtool.checkPermission(
                    'plonehrm: Modify manager checklist',
                    self):
                    raise Unauthorized
            else:
                if not mtool.checkPermission(
                    'plonehrm: Modify checklist',
                    self):
                    raise Unauthorized
            self.items.remove(item)

    def findItems(self, pattern, objects=False, **kwargs):
        """ Search in the item list. Pattern is the string that is
        searched in the items.
        A few keys are recognized in kwargs:
        - startswith: if set to True, search only items beginning with
          the pattern
        - endswith: if set to True, search only items ending with the
          pattern

        Returns the list of items corresponding to the search.

        objects parameter is used to know if we return the list
        of objects or just their texts.
        """

        starts_with = checkArgs('startswith', **kwargs)
        ends_with = checkArgs('endswith', **kwargs)

        # All items are searched.
        items = self.getAllItems(objects=True)

        results = []

        for item in items:
            # Checks if the pattern exists in the item
            added = not (item.text.find(pattern) == -1)

            if added and starts_with:
                added = item.text.startswith(pattern)

            if added and ends_with:
                added = item.text.endswith(pattern)

            if added:
                if objects:
                    results.append(item)
                else:
                    results.append(item.text)

        return tuple(results)

    def initializeArchetype(self, **kwargs):
        """Pre-populate the checklist.
        """

        BaseFolder.initializeArchetype(self, **kwargs)
        ct = getToolByName(self, 'portal_checklist')
        self.setAllItems(ct.getDefaultItems())
        self.setAllManagerItems(ct.getDefaultManagerItems())

registerType(Checklist, config.PROJECTNAME)
