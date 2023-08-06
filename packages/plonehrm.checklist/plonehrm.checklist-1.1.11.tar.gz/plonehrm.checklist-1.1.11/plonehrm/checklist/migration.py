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


def add_is_end_contract(context):
    """ Recreates checklist items to add the 'is_end_contract' property.
    """
    default_checklist = getToolByName(context, 'portal_checklist')

    for item in default_checklist.items:
        logger.info("Recreating '%s'" % item.text)
        item.__init__(item.text,
                      date=item.date,
                      isManager=item.isManager,
                      id=item.id)


def fix_default_checklist_items_without_ids(context):
    """Migration step used to fix default items without ids

    Apparently something is wrong in a previous migration so the
    checklist tool can end up with a few items that all have id 0.
    That wreaks havoc on the kss that is used for editing and adding
    items.
    """

    default_checklist = getToolByName(context, 'portal_checklist')
    ids = [x.id for x in default_checklist.items]
    if ids:
        next_id = max(ids) + 1
    else:
        next_id = 1
    double_ids = [x for x in ids if ids.count(x) != 1]
    if double_ids or default_checklist.next_id < next_id:
        # This means something is wrong.
        logger.info('Fixing portal_checklist items.')
        for new_id, item in enumerate(default_checklist.items):
            item.id = new_id
        default_checklist._set_next_id(next_id)
