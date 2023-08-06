from kss.core import kssaction, KSSView
from DateTime import DateTime
from AccessControl import Unauthorized

from Products.CMFCore.utils import getToolByName
from Products.SecureMailHost.SecureMailHost import EMAIL_RE
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
            except (ValueError, Unauthorized):
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

        # First, we check that all required items of the form were
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
                      'checklist_error_pastdate',
                      'checklist_error_date_required_notification',
                      'checklist_error_email_no_notification',
                      'checklist_error_invalid_email']:
            selector = core.getHtmlIdSelector(error)
            core.setAttribute(selector, 'class', 'dont-show')


        text = form['item_text']
        if not text:
            # Display an error message.
            selector = core.getHtmlIdSelector('checklist_error_notitle')
            core.setAttribute(selector, 'class', 'errormessage')
            errors = True

        # The item_due_date is not reliable as it is not always updated.
        notification = bool(form.get('item_notification', ''))
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
        elif notification:
            selector = core.getHtmlIdSelector(
                'checklist_error_date_required_notification')
            core.setAttribute(selector, 'class', 'errormessage')
            errors = True
        else:
            date = None

        email = form.get('item_notification_email')
        if email:
            if not notification:
                selector = core.getHtmlIdSelector(
                    'checklist_error_email_no_notification')
                core.setAttribute(selector, 'class', 'errormessage')
                errors = True
            if not EMAIL_RE.match(email):
                selector = core.getHtmlIdSelector('checklist_error_invalid_email')
                core.setAttribute(selector, 'class', 'errormessage')
                errors = True

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
            checklist.addItem(text, date=date,
                              notification=notification, email=email)
            message = translate(_(u'msg_checklist_item_added',
                                  u'Task has been added'),
                                target_language=self.lang)
        else:
            checklist.editItem(id, text, date=date,
                               notification=notification, email=email)
            message = translate(_(u'msg_checklist_item_edited',
                                  u'Task has been edited'),
                                target_language=self.lang)
        self.getCommandSet('plone').issuePortalMessage(message)
        self._updateViewlet('list')


class ChecklistToolKss(KSSView):
    """ Class managing KSS actions called on portal_checklist page.
    """

    @property
    def lang(self):
        props = getToolByName(self.context, 'portal_properties')
        return props.site_properties.getProperty('default_language')

    def refresh(self):
        """ Refreshes the view.
        """
        core = self.getCommandSet('core')
        selector = core.getHtmlIdSelector('checklist_tool_main')

        view = self.context.restrictedTraverse('@@checklisttool_edit')
        core.replaceInnerHTML(selector, view.index())

        # We add a simple div that will be triggered by KSS
        # and allows form tabbing.
        core.insertHTMLAsLastChild(selector, '<div id="kss-loaded"></div>')

    @kssaction
    def save(self):
        """ Process the form and update item values.
        """
        core = self.getCommandSet('core')
        form = self.request.form

        errors = []

        for field in form:
            #We check that it is an item text form (not a
            # checkbox for example.
            if not field.startswith('text_'):
                continue

            field_split = field.split('_')
            if not len(field_split) == 2:
                # Shall not happen
                continue

            item_id = int(field_split[1])
            item_text = form[field]

            if not item_text:
                errors.append('field_' + str(item_id))
                errors.append('error_empty_' + str(item_id))
                continue

            if not self.context.editItem(item_id, item_text):
                errors.append('field_' + str(item_id))
                errors.append('error_conflict_' + str(item_id))

        # Now we try to add the new items.
        if form['new_text_default']:
            add_to_all = 'add-to-all_default' in form
            if not self.context.addItem(form['new_text_default'],
                                        add_to_all):
                errors.append('field_new_default')
                errors.append('error_conflict_default')

        if form['new_text_manager']:
            add_to_all = 'add-to-all_manager' in form
            if not self.context.addManagerItem(form['new_text_manager'],
                                        add_to_all):
                errors.append('field_new_manager')
                errors.append('error_conflict_manager')

        if form['new_text_endcontract']:
            if not self.context.addEndContractItem(
                form['new_text_endcontract']):
                errors.append('field_new_endcontract')
                errors.append('error_conflict_endcontract')

        # We hide the previous errors.
        selector = core.getCssSelector('div.error')
        core.setAttribute(selector, 'class', 'field')

        selector = core.getCssSelector('p.clt_msg')
        core.setAttribute(selector, 'class', 'dont-show')

        if errors:
            for error in errors:
                selector = core.getHtmlIdSelector(error)
                if error.startswith('field_'):
                    core.setAttribute(selector, 'class', 'field error')
                else:
                    core.setAttribute(selector, 'class', 'clt_msg')

            message = _(u'errors_saving_portal_checklist',
                        u'Errors have been found while saving tasks.')
            msgtype = 'Error'
        else:
            message = _(u'success_saving_portal_checklist',
                        u'Tasks have been saved.')
            msgtype = 'Info'

            # We refresh the viewlet.
            self.refresh()

        message = translate(message, target_language=self.lang)
        self.getCommandSet('plone').issuePortalMessage(message,
                                                       msgtype=msgtype)

    @kssaction
    def cancel(self):
        """ Refreshes the page.
        """
        self.getCommandSet('plone').issuePortalMessage('')
        self.refresh()

    @kssaction
    def show_add_form(self, item_type):
        """ Shows a form to add a new item.
        item_type defines which form will be shown.
        """
        core = self.getCommandSet('core')

        item_type = item_type.split('_')[-1]
        if not item_type in ['default', 'manager', 'endcontract']:
            # Should not happen,
            return

        # We hide the button.
        selector = core.getHtmlIdSelector('command_new_' + item_type)
        core.setAttribute(selector, 'class', 'dont-show')

        # We show the form.
        selector = core.getHtmlIdSelector('field_new_' + item_type)
        core.setAttribute(selector, 'class', '')

    @kssaction
    def show_delete(self, item_id):
        """ Show confirmation form to delete an item.
        """
        core = self.getCommandSet('core')

        item_id = item_id.split('_')[-1]
        try:
            int(item_id)
        except:
            # Should not happen.
            return

        # Change div style
        selector = core.getHtmlIdSelector('field_' + item_id)
        core.setAttribute(selector, 'class', 'field confirm')

        # Show buttons and text.
        selector = core.getHtmlIdSelector('delete_form_' + item_id)
        core.setAttribute(selector, 'class', 'clt_msg')

    @kssaction
    def hide_delete(self, item_id):
        """ Hides the confirmation form to delete an item.
        """
        core = self.getCommandSet('core')

        item_id = item_id.split('_')[-1]
        try:
            int(item_id)
        except:
            # Should not happen.
            return

        # Change div style
        selector = core.getHtmlIdSelector('field_' + item_id)
        core.setAttribute(selector, 'class', 'field')

        # Show buttons and text.
        selector = core.getHtmlIdSelector('delete_form_' + item_id)
        core.setAttribute(selector, 'class', 'dont-show')

    @kssaction
    def delete_item(self, item_id):
        """ Deletes an item form the list.
        """
        core = self.getCommandSet('core')

        item_id = item_id.split('_')[-1]
        try:
            int(item_id)
        except:
            # Should not happen.
            return

        self.context.deleteItem(int(item_id))

        message = _(u'success_deleting_portal_checklist',
                    u'Task has been deleted.')

        message = translate(message, target_language=self.lang)
        self.getCommandSet('plone').issuePortalMessage(message)

        selector = core.getHtmlIdSelector('field_' + item_id)
        core.deleteNode(selector)
