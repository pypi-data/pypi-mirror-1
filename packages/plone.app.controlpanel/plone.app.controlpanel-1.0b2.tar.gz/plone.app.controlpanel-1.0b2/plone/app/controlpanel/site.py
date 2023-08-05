from zope.app.form.browser import TextAreaWidget
from zope.interface import Interface
from zope.component import adapts
from zope.component import getUtility
from zope.formlib.form import FormFields
from zope.interface import implements
from zope.schema import Bool
from zope.schema import Text
from zope.schema import TextLine
from zope.schema import SourceText

from Products.CMFCore.interfaces import IPropertiesTool
from Products.CMFDefault.formlib.schema import ProxyFieldProperty
from Products.CMFDefault.formlib.schema import SchemaAdapterBase
from Products.CMFPlone import PloneMessageFactory as _
from Products.CMFPlone.interfaces import IPloneSiteRoot
from Products.CMFPlone.utils import safe_unicode

from form import ControlPanelForm

class ISiteSchema(Interface):

    site_title = TextLine(title=_(u'Site title'),
                          description=_(u"""The title of your site."""),
                          default=u'')

    site_description = Text(title=_(u'Site description'),
                           description=_(u"The site description is available "
                               "in syndicated content and elsewhere. Keep it "
                               "brief."),
                           default=u'',
                           required=False)

    visible_ids = Bool(title=_(u'Show "Short Name" on content?'),
                       description=_(u"Display and allow users to edit the "
                           "'Short name' content identifiers, which form the "
                           "URL part of a content item's address. Once "
                           "enabled, users will then be able to enable this "
                           "option in their preferences."),
                       default=False)

    enable_link_integrity_checks = Bool(title=_(u'Enable link integrity checks'),
                          description=_(u"Determines if the users should get "
                              "warnings when they delete or move content that "
                              "is linked from inside the site"),
                          default=True)

    ext_editor = Bool(title=_(u'Enable External Editor feature'),
                          description=_(u"Determines if the external editor "
                              "feature is enabled. This feature requires a "
                              "special client-side application installed. The "
                              "users also have to enable this in their "
                              "preferences."),
                          default=False)

    enable_sitemap = Bool(title=_(u'Provide sitemap.xml.gz in the portal root'),
                          description=_(u"A sitemap.xml.gz file might be "
                              "useful for Google and lists all your content "
                              "along with modification dates. Please note that "
                              "generating the sitemap is an expensive "
                              "operation which can be abused to slow down "
                              "your site."),
                          default=False)
                          
    webstats_js = SourceText(title=_(u'JavaScript for web statistics support'),
                        description=_(u"For enabling web statistics support "
                            "for e.g. Google Analytics. Look at "
                            "http://plone.org for snippets which you can paste "
                            "here. Do not paste Google Analytics code here "
                            "directly; it will not work."),
                        default=u'',
                        required=False)


class SiteControlPanelAdapter(SchemaAdapterBase):

    adapts(IPloneSiteRoot)
    implements(ISiteSchema)

    def __init__(self, context):
        super(SiteControlPanelAdapter, self).__init__(context)
        self.portal = context
        pprop = getUtility(IPropertiesTool)
        self.context = pprop.site_properties
        self.encoding = pprop.site_properties.default_charset

    def get_site_title(self):
        title = getattr(self.portal, 'title', u'')
        return safe_unicode(title)

    def set_site_title(self, value):
        self.portal.title = value.encode(self.encoding)

    def get_site_description(self):
        description = getattr(self.portal, 'description', u'')
        return safe_unicode(description)

    def set_site_description(self, value):
        if value is not None:
            self.portal.description = value.encode(self.encoding)
        else:
            self.portal.description = ''

    def get_webstats_js(self):
        description = getattr(self.context, 'webstats_js', u'')
        return safe_unicode(description)

    def set_webstats_js(self, value):
        if value is not None:
            self.context.webstats_js = value.encode(self.encoding)
        else:
            self.context.webstats_js = ''

    site_title = property(get_site_title, set_site_title)
    site_description = property(get_site_description, set_site_description)
    webstats_js = property(get_webstats_js, set_webstats_js)

    visible_ids = ProxyFieldProperty(ISiteSchema['visible_ids'])
    enable_link_integrity_checks = ProxyFieldProperty(ISiteSchema['enable_link_integrity_checks'])
    ext_editor = ProxyFieldProperty(ISiteSchema['ext_editor'])
    enable_sitemap = ProxyFieldProperty(ISiteSchema['enable_sitemap'])


class SmallTextAreaWidget(TextAreaWidget):

    height = 5


class SiteControlPanel(ControlPanelForm):

    form_fields = FormFields(ISiteSchema)
    form_fields['site_description'].custom_widget = SmallTextAreaWidget

    label = _("Site settings")
    description = _("Site-wide settings.")
    form_name = _("Site details")
