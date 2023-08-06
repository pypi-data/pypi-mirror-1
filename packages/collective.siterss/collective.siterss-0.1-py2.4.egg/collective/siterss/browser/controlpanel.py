from zope import schema
from zope.component import adapts, getMultiAdapter
from zope.formlib.form import FormFields

from zope.interface import implements
from zope.interface import Interface
from plone.app.form.widgets.uberselectionwidget import UberMultiSelectionWidget
from plone.app.vocabularies.catalog import SearchableTextSourceBinder
from collective.siterss.browser.catalog_vocabulary import MineSearchableTextSourceBinder

from Products.CMFCore.utils import getToolByName
from Products.CMFDefault.formlib.schema import SchemaAdapterBase
from Products.CMFDefault.formlib.schema import ProxyFieldProperty
from Products.CMFPlone.interfaces import IPloneSiteRoot
from Products.ATContentTypes.interface.topic import IATTopic

from plone.app.controlpanel.form import ControlPanelForm

from collective.siterss import siterssMessageFactory as _

class ISiteRSSSchema(Interface):
    """
    """
    
    rss_items = schema.List(
                    title=_(u"Site items"),
                    description=_(u'help_site_rss_items',
                                  default=u"You may search for and choose a "
                                            "Smart Folder "
                                            "to act as the source of RSS feed. "
                                            "Use search box below to search "
                                            "items in the portal and select "
                                            "items you want to provide as RSS "
                                            "feeds."),
                    required=False,
                    value_type=schema.Choice(
                                    source=MineSearchableTextSourceBinder({'object_provides':IATTopic.__identifier__},
                                                      default_query='path:')
                                            )
                )

    additional_rss_items = schema.List(
                    title=_(u"Additional RSS items"),
                    description=_(u'help_additional_rss_items',
                                  default=u"You may enter additional RSS items in the form: url<space>title. Url has to be full URL including http:// prefix and must point to the RSS feed."),
                    required=False,
                    value_type=schema.TextLine(title=_(u"Additional item"), required=False)
                )
   
class SiteRSSControlPanelAdapter(SchemaAdapterBase):

    adapts(IPloneSiteRoot)
    implements(ISiteRSSSchema)

    def __init__(self, context):
        super(SiteRSSControlPanelAdapter, self).__init__(context)
        self.portal = context
        pprop = getToolByName(self.portal, 'portal_properties')
        self.context = pprop.site_properties

    def get_rss_items(self):
        # uberselection widget does not like empty values
        rss_items = [x for x in getattr(self.context, 'site_rss_items', []) if x]
        return rss_items

    def set_rss_items(self, value):
        if value is not None:
            self.context.site_rss_items = value
        else:
            self.context.site_rss_items = []

    def get_additional_rss_items(self):
        rss_items = [x for x in getattr(self.context, 'additional_rss_items', []) if x]
        return rss_items

    def set_additional_rss_items(self, value):
        if value is not None:
            self.context.additional_rss_items = value
        else:
            self.context.additional_rss_items = []

    rss_items = property(get_rss_items, set_rss_items)
    additional_rss_items =  property(get_additional_rss_items, set_additional_rss_items)
    
class SiteRSSControlPanel(ControlPanelForm):

    form_fields = FormFields(ISiteRSSSchema)
    form_fields['rss_items'].custom_widget = UberMultiSelectionWidget

    label = _("Site RSS settings")
    description = _("Setup Site RSS feeds.")
    form_name = _("Site RSS settings")

