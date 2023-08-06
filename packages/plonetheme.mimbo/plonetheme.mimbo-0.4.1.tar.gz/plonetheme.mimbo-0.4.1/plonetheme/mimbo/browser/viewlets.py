from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.layout.viewlets.common import ViewletBase

from zope.component import getMultiAdapter
from AccessControl import getSecurityManager
from Products.CMFCore.utils import getToolByName

class PersonalBarViewlet(ViewletBase):
    render = ViewPageTemplateFile('personal_bar.pt')

    def update(self):
        super(PersonalBarViewlet, self).update()

        context_state = getMultiAdapter((self.context, self.request),
                                        name=u'plone_context_state')
        tools = getMultiAdapter((self.context, self.request), name=u'plone_tools')

        sm = getSecurityManager()

        self.user_actions = context_state.actions().get('user', None)

        plone_utils = getToolByName(self.context, 'plone_utils')
        self.getIconFor = plone_utils.getIconFor

        self.anonymous = self.portal_state.anonymous()

        if not self.anonymous:

            member = self.portal_state.member()
            userid = member.getId()

            if sm.checkPermission('Portlets: Manage own portlets', self.context):
                self.homelink_url = self.site_url + '/dashboard'
            else:
                if userid.startswith('http:') or userid.startswith('https:'):
                    self.homelink_url = self.site_url + '/author/?author=' + userid
                else:
                    self.homelink_url = self.site_url + '/author/' + quote_plus(userid)

            member_info = tools.membership().getMemberInfo(member.getId())
            # member_info is None if there's no Plone user object, as when
            # using OpenID.
            if member_info:
                fullname = member_info.get('fullname', '')
            else:
                fullname = None
            if fullname:
                self.user_name = fullname
            else:
                self.user_name = userid

class FooterViewlet(ViewletBase):
    render = ViewPageTemplateFile('footer.pt')

