from zope.interface import implements
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.portlets import base
from Products.CMFPlone import PloneMessageFactory as _
from Products.remember.interfaces import IReMember

class IMemberPortlet(IPortletDataProvider):
    """A portlet which displays the OpenID info for a Remember member
    object.
    """


class Assignment(base.Assignment):
    implements(IMemberPortlet)

    title = _(u'OpenID Account')


class Renderer(base.Renderer):

    def __init__(self, context, request, view, manager, data):
        base.Renderer.__init__(self, context, request, view, manager, data)

    def show(self):
        if not IReMember.providedBy(self.context):
            return False
        page = self.request.get('URL', '').split('/')[-1]
        return page.endswith('edit')

    def openid_urls(self):
        return getattr(self.context, '_openid_urls', [])

    render = ViewPageTemplateFile('member.pt')


class AddForm(base.NullAddForm):

    def create(self):
        return Assignment()
