__author__ = """unknown <unknown>"""
__docformat__ = 'plaintext'

from DateTime import DateTime

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
from zope.annotation.interfaces import IAnnotations
from persistent.list import PersistentList
from persistent.dict import PersistentDict
from persistent import Persistent

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
                 checked = False,
                 isManager = False,
                 link_url=None,
                 link_title=None,
                 id=0):
        self.text = text
        self.date = date
        self.checked = checked
        self.isManager = isManager
        self.link_url = link_url
        self.link_title = link_title
        self.id = 0

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
            self.metadata['items'] = PersistentList()

        return self.metadata['items']

    def _filterItems(self, objects=False, **kwargs):
        """ Filter items depending on some criteria in kwargs:
        - checked: if set, only returns checked or unchecked items.
        - isManager: if set, only returns manager items or all items.

        The object item is used to know if the method returns a list of
        CheckListItem() objects or just the list of their texts.
        """
        items = []

        if 'checked' in kwargs:
            check_filter = True
            checked = kwargs['checked']
        else:
            check_filter = False
            checked = False

        if 'isManager' in kwargs:
            manager_filter = True
            manager = kwargs['isManager']
        else:
            manager_filter = False
            manager = False

        for item in self.items:
            append = True

            # If the checked filter is set and the
            # item doesnot correspond to the filter, we
            # do not append the item.
            if check_filter and \
               not item.checked == checked:
                append = False

            # Same thing for the manager filter
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
        """ Same principle than the getAllItems() method,
        except that it only fetches items for which
        the 'checked' property is set to True.
        """
        return tuple(self._filterItems(objects, checked=True, isManager=False))

    def setCheckedItems(self, items):
        """ Same principle than setAllItems, but creates checked items.
        """
        self._deleteItems(isManager=False, checked=True)
        for item in items:
            self.addItem(item, checked=True)

    def getCheckedManagerItems(self, objects=False):
        """ Same principle than the getCheckedItems() method,
        except that it filters only manager items.
        """
        return tuple(self._filterItems(objects, checked=True, isManager=True))

    def setCheckedManagerItems(self, items):
        """ Same principle than setAllmanagerItems, but creates checked
        items.
        """
        self._deleteItems(isManager=True, checked=True)
        for item in items:
            self._addItem(item, checked=True, isManager=True)

    def remainingItems(self, objects=False):
        """ Works the same way than the getCheckedItems(),
        except that it returns items that have not been checked.
        """
        return tuple(self._filterItems(objects, checked=False, isManager=False))

    def remainingManagerItems(self, objects=False):
        """ Same as remainingItems() but for manager items.
        """
        return tuple(self._filterItems(objects, checked=False, isManager=True))

    def remainingAllItems(self):
        """ Returns all remaining items (manager and not manager.)
        It first displays non manager items, then manager items.
        """
        items = self._filterItems(objects=True, isManager=False, checked=False)
        items.extend(self._filterItems(objects=True, isManager=True, checked=False))
        return items

    def _addItem(self,
                 text,
                 date=None,
                 checked=False,
                 isManager=False,
                 link_url=None,
                 link_title=None):
        """ Adds a new item to the list. This method
        shall not be called directly. Items should be added
        with addItem() or addManagerItem().
        """
        item = CheckListItem(text, date, checked, isManager,
                             link_url, link_title)
        self.items.append(item)

        # We set the item's id.
        self.items[-1].id = len(self.items)

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
                link_url=None, link_title=None, checked=False):
        """Add an item to the list of to-check items.
        """
        if not self._existsItem(text):
            self._addItem(text, date=date, link_url=link_url,
                          checked=checked, link_title=link_title)

    def addManagerItem(self, text, date=None,
                       link_url=None, link_title = None, checked=False):
        """Add an item to the list of manager to-check items.
        """
        if not self._existsItem(text):
            self._addItem(text, isManager=True,
                          date=date, link_url=link_url,
                          checked=checked, link_title=link_title)

    def checkItem(self, id=None, text=None):
        """ Checks an item, found by its id or name.
        """
        for item in self.items:
           if item.id == id or item.text == text:
               item.checked = True
               return

    def editItem(self, id, text, date=None, link_url=None, link_title=None):
        """ Edit properties of an item.
        """
        for item in self.items:
            if item.id == id:
                item.text = text
                item.date = date
                item.link_url = link_url
                item.link_title = link_title
                return

    def deleteItem(self, text):
        """ Removes an item from the list.
        """
        item = self.findItem(text=text)
        if item:
            self.items.remove(item)

    def findItems(self, pattern, objects=False, **kwargs):
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

        objects parameter is used to know if we return the list
        of objects or just their texts.
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
            # objects is set to True as we need objects
            # to performs the search.
            items = self.getCheckedItems(objects=True)

        # Only remaining items are searched.
        if unchecked:
            items = self.remainingItems(objects=True)

        # Every items are searched.
        if not checked and not unchecked:
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
