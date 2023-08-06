def handleHRMModuleEventForEmployee(object, event):
    """Add a (manager) checklist item to the object.
    """
    if event.for_manager:
        object.checklist.addManagerItem(event.message)
    else:
        object.checklist.addItem(event.message)
