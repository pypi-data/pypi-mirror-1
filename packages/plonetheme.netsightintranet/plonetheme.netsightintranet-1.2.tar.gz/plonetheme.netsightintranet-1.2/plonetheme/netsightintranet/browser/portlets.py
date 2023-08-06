from plone.app.portlets.portlets import recent
from plone.app.portlets.portlets import news
from plone.app.portlets.portlets import navigation
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.layout.navigation.navtree import buildFolderTree
from zope.component import getMultiAdapter

class NavigationRenderer(navigation.Renderer):

    @property
    def available(self):
        # Always available
        return True

    def isHome(self):
        portal_state = getMultiAdapter((self.context, self.request),
                                       name=u'plone_portal_state')
        purl = '%s/' % portal_state.portal().absolute_url()
        curl = self.request.get('ACTUAL_URL', '')
        return purl == curl

    def getSubNavigation(self):
        query = {}
        query['path'] = {
            'query' : '/'.join(self.context.getPhysicalPath()),
            'navtree' : 1,
            'navtree_start' : 2,
            }

        query['exclude_from_nav'] = [False, None, ]

        tree = buildFolderTree(self.context, obj=self.context, query=query)

        if tree and tree.has_key('children'):
            return tree['children']
        else:
            return []

    def getSubSection(self):
        context = self.context
        if self.isHome():
            portal_state = getMultiAdapter((self.context, self.request),
                                           name=u'plone_portal_state')
            return portal_state.portal()
        
        sectionpath = '/'.join(context.getPhysicalPath()[:3])
        section = context.restrictedTraverse(sectionpath)
        return section

    _template = ViewPageTemplateFile('templates/navigation.pt')
    recurse = ViewPageTemplateFile('templates/navigation_recurse.pt')



class RecentRenderer(recent.Renderer):

    _template = ViewPageTemplateFile('templates/recent.pt')

class NewsRenderer(news.Renderer):

    _template = ViewPageTemplateFile('templates/news.pt')
