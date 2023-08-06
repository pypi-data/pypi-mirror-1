from zope.component import getUtility
from zope.interface import implements, Interface
from plone.app.layout.viewlets import ViewletBase
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile
from Products.CMFPlone.interfaces import IPloneSiteRoot
from Products.CMFPlone.utils import safe_unicode
from Products.CMFCore.utils import getToolByName

from collective.siterss.browser.controlpanel import ISiteRSSSchema

class ISiteRSSViewlet(Interface):
    
    def links():
        """ return all associated Smart folders """

class SiteRSSViewlet(ViewletBase):
    implements(ISiteRSSViewlet)
    
    _links = None
    
    @property
    def prefs(self):
        portal = getUtility(IPloneSiteRoot)
        return ISiteRSSSchema(portal)

    def _update_links(self):
        # get urls
        items = self.prefs.rss_items
        additional_items = self.prefs.additional_rss_items
        if not (items or additional_items):
            self.allowed = False
        else:
            self.allowed = True
            portal = getUtility(IPloneSiteRoot)
            request = self.request
            # using portal_catalog to be able to get the Title
            catalog = getToolByName(self, 'portal_catalog')
            self._links = []
            portal_id = portal.getId()
            for item in items:
                if item.strip().startswith('/'):
                    # add portal ID before item
                    item = "/" + portal_id + item
                    topics = catalog(path={'query':item, 'depth':0})
                    if len(topics)==1:
                        self._links.append({'url':topics[0].getURL()+'/RSS', 'title':safe_unicode(topics[0].Title)})
            for item in additional_items:
                if item:
                    try:
                        url, title = item.split(' ', 1)
                    except ValueError:
                        continue
                    self._links.append({'url':url, 'title':title})

    def links(self):
        return self._links

    def update(self):
        super(SiteRSSViewlet, self).update()
        if self._links is None:
            self._update_links()
            

    render = ViewPageTemplateFile('rsslinks.pt')