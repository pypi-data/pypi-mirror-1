from zope.interface import implements
from zope.component import getMultiAdapter

from plone.fieldsets.form import FieldsetsEditForm
from zope.formlib import form

from Products.CMFPlone import PloneMessageFactory as _
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.statusmessages.interfaces import IStatusMessage

from plone.app.form import named_template_adapter
from plone.app.form.validators import null_validator

from plone.app.controlpanel.interfaces import IPloneControlPanelForm

class ControlPanelForm(FieldsetsEditForm):
    """A simple form to be used as a basis for control panel screens."""

    implements(IPloneControlPanelForm)

    @form.action(_(u'Save'))
    def handle_edit_action(self, action, data):
        if form.applyChanges(self.context, self.form_fields, data,
                             self.adapters):
            self.status = _("Changes saved.")
        else:
            self.status = _("No changes made.")

    @form.action(_(u'Cancel'), validator=null_validator)
    def handle_cancel_action(self, action, data):
        IStatusMessage(self.request).addStatusMessage(_("Changes canceled."),
                                                      type="info")
        url = getMultiAdapter((self.context, self.request),
                              name='absolute_url')()
        self.request.response.redirect(url + '/plone_control_panel')
        return ''

_template = ViewPageTemplateFile('control-panel.pt')
controlpanel_named_template_adapter = named_template_adapter(_template)
