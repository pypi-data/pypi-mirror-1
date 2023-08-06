from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.layout.viewlets.common import ViewletBase
from zope.component import getMultiAdapter

class NonzeroLogoViewlet(ViewletBase):
    render = ViewPageTemplateFile('nonzero_logo.pt')

    def update(self):
        portal_state = getMultiAdapter((self.context, self.request),
                                            name=u'plone_portal_state')

        portal = portal_state.portal()
        
        self.portal = portal.absolute_url()
        self.portal_title = portal_state.portal_title()
        self.portal_desc = portal.description