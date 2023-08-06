from zope.interface import Interface


class IChecklistToolView(Interface):
    """ A view for configuring the checklist settings
    """

    def form_action():
        """Return action for the checklist form.
        """

    def form_handle():
        """Return if the form has updated anything"""


class IChecklistView(Interface):
    """ A view for handling checklists
    """

    def items_left():
        """Return if there are any items left to display"""

    def manager_items_left():
        """Return if there are any manager items left to display"""

    def any_items_left():
        """Return if there are items or manager items left to display"""

    def canEditItems():
        """Return if we can edit the items.
        """

    def canEditManagerItems():
        """Return if we can edit the manager items.
        """
