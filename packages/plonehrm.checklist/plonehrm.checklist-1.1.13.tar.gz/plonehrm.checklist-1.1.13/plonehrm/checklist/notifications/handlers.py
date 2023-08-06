def handleHRMModuleEventForEmployee(object, event):
    """Add a (manager) checklist item to the object.
    """
    if hasattr(event, 'link_url'):
        link_url = event.link_url
    else:
        link_url = None
    if hasattr(event, 'link_title'):
        link_title = event.link_title
    else:
        link_title = None
    if hasattr(event, 'date'):
        date = event.date
    else:
        date = None

    if event.for_manager:
        object.checklist.addManagerItem(
            event.message, date=date,
            link_url=link_url, link_title = link_title)
    else:
        object.checklist.addItem(
            event.message, date=date,
            link_url=link_url, link_title = link_title)
