from kss.core import kssaction, KSSView
from DateTime import DateTime

from Products.CMFCore.utils import getToolByName
from zope.i18n import translate

from plonehrm.checklist import ChecklistMessageFactory as _

class ChecklistKss(KSSView):

    @property
    def lang(self):
        props = getToolByName(self.context, 'portal_properties')
        return props.site_properties.getProperty('default_language')


    def _updateViewlet(self, view_mode, item=None):
        """ Factorisation of the code updating viewlet content.
        """
        # First, we get the viewlet manager.
        view = self.context.restrictedTraverse('@@plonehrm.checklist')

        # We configure it.
        view.view_mode = view_mode
        view.editedItem = item

        # We get the content displayed by in the viewlet.
        rendered = view.render()

        # We replace the content of the viewlet by the new one.
        core = self.getCommandSet('core')
        selector = core.getHtmlIdSelector('checklist')
        core.replaceHTML(selector, rendered)

    @kssaction
    def display_list(self):
        """ Shows the list of items left in the viewlet.
        """
        self.getCommandSet('plone').issuePortalMessage('')
        self._updateViewlet('list')

    @kssaction
    def display_add_form(self):
        """ Shows the form to add a new item.
        """
        self._updateViewlet('form_new')

    @kssaction
    def display_edit_form(self, item):
        """ Shows the form to add a new item.
        """

        item_id = int(item.split('-')[1])
        checklist = self.context.checklist
        
        self._updateViewlet('form_edit', checklist.findItem(id=item_id))


    @kssaction
    def update_list(self):
        """ Updates the list of items (make them checked)
        """
        form = self.request.form
        checklist = self.context.checklist

        items_count = 0
        for key in form:
            try:
                id = int(key)
                checklist.checkItem(id=id)
                items_count += 1
            except ValueError:
                pass

        if items_count:
            # Display the info message.
            if items_count == 1:
                message = translate(_(u'msg_checklist_update_one_item',
                                      u'The task has been marked as done'),
                                    target_language=self.lang)
            else:
                message = translate(_(u'msg_checklist_update_items',
                                      u'The tasks have been marked as done'),
                                    target_language=self.lang)
        else:
            # Hides the info viewlet.
            message = ''

        self.getCommandSet('plone').issuePortalMessage(message)

        self._updateViewlet('list')

    @kssaction
    def add_or_edit_item(self):
        """ This method allows to add or edit an item.
        The behaviour will be changed depending on the
        presence of the 'item_id' field in the
        submitted form.
        """
        
        form = self.request.form
        checklist = self.context.checklist

        errors = False

        # First, we check that all required items of the form wer
        # submitted to avoid key errors.
        keys = ['item_id', 'item_text', 'item_due_date',
                'item_due_date_year']
        for k in keys:
            if not k in form:
                return

        core = self.getCommandSet('core')

        try:
            id = int(form['item_id'])
        except ValueError:
            # The id was not submitted, that means that a
            # new item is created.
            id = None

        # We hide the previous errors.
        for error in ['checklist_error_notitle',
                      'checklist_error_pastdate']: 
            selector = core.getHtmlIdSelector(error)
            core.setAttribute(selector, 'class', 'dont-show')
           

        text = form['item_text']
        if not text:
            # Display an error message.
            selector = core.getHtmlIdSelector('checklist_error_notitle')
            core.setAttribute(selector, 'class', 'errormessage')
            errors = True

        # The item_due_date is not reliable as it is not always updated.
        if form.get('item_due_date_year', '0000') != '0000':
            year = int(self.request.get('item_due_date_year'))
            month = int(self.request.get('item_due_date_month'))
            day = int(self.request.get('item_due_date_day'))
            try:
                date = DateTime(year, month, day)
            except:
                date = None
            if date and date.isPast() and not date.isCurrentDay():
                # Displays an error message
                selector = core.getHtmlIdSelector('checklist_error_pastdate')
                core.setAttribute(selector, 'class', 'errormessage')
                errors = True
        else:
            date = None

        if errors:
            if id is None:
                message=_(u'msg_checklist_error_creation',
                          u'Errors have been found when creating the task')
            else:
                message=_(u'msg_checklist_error_edition',
                          u'Errors have been found when editing the task')

            message = translate(message, target_language=self.lang)            
            self.getCommandSet('plone').issuePortalMessage(message,
                                                           msgtype='Error')
            return

        
        if id is None:
            checklist.addItem(text, date=date)
            message = translate(_(u'msg_checklist_item_added',
                                  u'Task has been added'),
                                target_language=self.lang)
        else:            
            checklist.editItem(id, text, date=date)
            message = translate(_(u'msg_checklist_item_edited',
                                  u'Task has been edited'),
                                target_language=self.lang)
        self.getCommandSet('plone').issuePortalMessage(message)
        self._updateViewlet('list')

