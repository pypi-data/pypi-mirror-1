import logging
from Products.CMFCore.utils import getToolByName

logger = logging.getLogger("plonehrm.checklist")


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


    logger.info("Found %d checklists.", len(checklists))
    for checklist in checklists:
        try:
            checklist = checklist.getObject()
        except (AttributeError, KeyError):
            logger.warn("Error getting object at %s", checklist.getURL())
            continue

        all_items = checklist.getRawAllItems()
        checked_items = checklist.getRawCheckedItems()
        all_manager_items = checklist.getRawAllManagerItems()
        checked_manager_items = checklist.getRawCheckedManagerItems()

        for item in all_items:
            if not item in checked_items:
                checklist.addItem(item)

        for item in all_manager_items:
            if not item in checked_manager_items:
                checklist.addManagerItem(item)

        # We update the items ids.
        for i in range(0, len(checklist.items)):
            checklist.items[i].id = i+1

        fields = ['allItems', 'checkedItems',
                  'allManagerItems', 'checkedManagerItems']
        for field in fields:
            checklist.getField(field).set(checklist, [])


def delete_checked_items(context):
    """ Migration step used to delete checked items.

    Previously we wanted to keep items that we checked, but now we
    just delete them.
    """

    catalog = getToolByName(context, 'portal_catalog')
    query = {'portal_type': 'Checklist'}
    checklists = catalog(query)

    logger.info("Found %d checklists.", len(checklists))
    for checklist in checklists:
        try:
            checklist = checklist.getObject()
        except (AttributeError, KeyError):
            logger.warn("Error getting object at %s", checklist.getURL())
            continue

        # We need to make a copy of the list otherwise the for loop
        # will start acting funky when items have been removed.
        items = checklist.items[:]
        logger.info('Checklist has %d items.', len(items))
        removed = 0
        for item in items:
            if hasattr(item, 'checked') and item.checked:
                logger.info('Removing checked item %s', item.text)
                checklist.items.remove(item)
                removed += 1
        logger.info('Removed %d checked items.', removed)
