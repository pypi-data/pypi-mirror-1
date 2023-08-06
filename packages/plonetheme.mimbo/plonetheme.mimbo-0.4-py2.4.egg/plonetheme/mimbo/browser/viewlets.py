from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.layout.viewlets.common import ViewletBase

class FooterViewlet(ViewletBase):
    render = ViewPageTemplateFile('footer.pt')