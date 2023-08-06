from zope.component import getMultiAdapter
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.layout.viewlets.common import ViewletBase

class PortalTitleViewlet(ViewletBase):
    render = ViewPageTemplateFile('portal_title_viewlet.pt')

    def update(self):
        self.portal_state = getMultiAdapter((self.context, self.request),
                                            name=u'plone_portal_state')
        self.portal_title = self.portal_state.portal_title
        self.portal_description = self.portal_state.portal().Description()
