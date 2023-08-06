from Products.CMFCore.utils import getToolByName
from plonehrm.checklist.content.checklist import Checklist
from plonehrm.checklist.content.tool import ChecklistTool

from Acquisition import aq_inner

def migrate_checklist_items(context):
    """ Migration step used to transform old checklist items (in Archetype
    fields) to new checklist items (in PersistentList).
    This tool updates employee's checklists and default checklists.
    """

    # First, we update default checklists.
    default_checklist = getToolByName(context, 'portal_checklist')
    
    for item in default_checklist.getRawDefaultItems():
        default_checklist.addItem(item)

    for mItem in default_checklist.getRawDefaultManagerItems():
        default_checklist.addManagerItem(mItem)


    # We update the user's checklists.
    catalog = getToolByName(context, 'portal_catalog')
    query = {'portal_type': 'Checklist'}
    checklists = catalog(query)

    fields = ['defaultItems', 'defaultManagerItems']
    for field in fields:
        default_checklist.getField(field).set(default_checklist, [])


    for checklist in checklists:
        checklist = checklist.getObject()
        
        all_items = checklist.getRawAllItems()
        checked_items = checklist.getRawCheckedItems()
        all_manager_items = checklist.getRawAllManagerItems()
        checked_manager_items = checklist.getRawCheckedManagerItems()
        
        for item in all_items:
            checked = item in checked_items
            checklist.addItem(item, checked=checked)

        for item in all_manager_items:
            checked = item in checked_manager_items
            checklist.addManagerItem(item, checked=checked)

        # We update the items ids.
        for i in range(0, len(checklist.items)):
            checklist.items[i].id = i+1

        fields = ['allItems', 'checkedItems',
                  'allManagerItems', 'checkedManagerItems']
        for field in fields:
            checklist.getField(field).set(checklist, [])
            
