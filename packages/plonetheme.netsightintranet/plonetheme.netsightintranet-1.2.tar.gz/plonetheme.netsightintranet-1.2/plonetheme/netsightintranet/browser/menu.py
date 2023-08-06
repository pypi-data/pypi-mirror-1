from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.contentmenu.view import ContentMenuProvider
from Acquisition import Explicit
from zope.component import getMultiAdapter, queryMultiAdapter, getUtility
from Acquisition import aq_inner

class IntranetContentMenuProvider(ContentMenuProvider):
    def getCurrentObjectUrl(self):
        context_state = getMultiAdapter((aq_inner(self.context), self.request), name=u'plone_context_state')
        return context_state.canonical_object_url()

    render = ZopeTwoPageTemplateFile('templates/contentmenu.pt')

class IntranetContentViewProvider(Explicit):

    def __init__(self, context, request, view):
        self.__parent__ = view
        self.view = view
        self.context = context
        self.request = request


    def update(self):
        pass  

    render = ViewPageTemplateFile('templates/contentviews.pt')
