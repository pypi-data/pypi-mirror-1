import os
from cgi import escape

from plone.app.form.validators import null_validator
from plone.fieldsets.form import FieldsetsEditForm
from zope.component import adapts
from zope.formlib import form
from zope.interface import Interface
from zope.interface import implements
from zope.schema import Int

from Acquisition import aq_inner
from Products.CMFCore.utils import getToolByName
from Products.CMFDefault.formlib.schema import SchemaAdapterBase
from Products.CMFPlone import PloneMessageFactory as _
from Products.CMFPlone.interfaces import IPloneSiteRoot
from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile

from plone.app.controlpanel.interfaces import IPloneControlPanelForm


class IMaintenanceSchema(Interface):

    days = Int(title=_(u"Days of object history to keep after packing"),
        description=_(u"You should pack your database regularly. This number"
                       "indicates how many days of undo history you want to "
                       "keep. It is unrelated to versioning, so even if you"
                       "pack the database, the history of the content changes"
                       "will be kept. Recommended value is 7 days."),
        default=7,
        required=True)


class MaintenanceControlPanelAdapter(SchemaAdapterBase):

    adapts(IPloneSiteRoot)
    implements(IMaintenanceSchema)

    def __init__(self, context):
        pprop = getToolByName(context, 'portal_properties')
        self.context = pprop.site_properties

    def get_days(self):
        return self.context.number_of_days_to_keep

    def set_days(self, value):
        if isinstance(value, basestring):
            value = int(value)
        self.context.number_of_days_to_keep = value

    days = property(get_days, set_days)


class MaintenanceControlPanel(FieldsetsEditForm):
    """A simple form to pack the databases."""

    implements(IPloneControlPanelForm)

    template = ZopeTwoPageTemplateFile('maintenance.pt')
    form_fields = form.FormFields(IMaintenanceSchema)
    label = _(u'Maintenance')
    description = _(u"Zope server and site maintenance options.")
    form_name = _(u'Zope Database Packing')

    @form.action(_(u'Pack'))
    def handle_edit_action(self, action, data):
        form.applyChanges(self.context, self.form_fields, data, self.adapters)
        value = data.get('days', None)
        # skip the actual pack method in tests
        if value is not None and isinstance(value, int) and value >= 0:
            context = aq_inner(self.context)
            cpanel = context.unrestrictedTraverse('/Control_Panel')
            cpanel.manage_pack(days=value, REQUEST=None)
        self.status = _(u'Packed the database.')

    @form.action(_(u'Shutdown'), validator=null_validator)
    def handle_shutdown_action(self, action, data):
        context = aq_inner(self.context)
        cpanel = context.unrestrictedTraverse('/Control_Panel')
        result = cpanel.manage_shutdown()
        return result

    @form.action(_(u'Restart'), validator=null_validator)
    def handle_restart_action(self, action, data):
        context = aq_inner(self.context)
        cpanel = context.unrestrictedTraverse('/Control_Panel')
        url = self.request.get('URL')
        result = cpanel.manage_restart(url)
        return """<html>
        <head><meta HTTP-EQUIV=REFRESH CONTENT="10; URL=%s">
        </head>
        <body>Zope is restarting</body></html>
        """ % escape(url, 1)

    def isRestartable(self):
        if os.environ.has_key('ZMANAGED'):
            return True
        return False

    def isDevelopmentMode(self):
        qi = getToolByName(self.context, 'portal_quickinstaller')
        return qi.isDevelopmentMode()

    def coreVersions(self):
        mt = getToolByName(self.context, 'portal_migration')
        versions = mt.coreVersions()
        versions['Instance'] = versions['Plone Instance']
        return versions

    def processTime(self):
        context = aq_inner(self.context)
        cpanel = context.unrestrictedTraverse('/Control_Panel')
        return cpanel.process_time()

    def dbSize(self):
        context = aq_inner(self.context)
        cpanel = context.unrestrictedTraverse('/Control_Panel')
        return cpanel.db_size()
