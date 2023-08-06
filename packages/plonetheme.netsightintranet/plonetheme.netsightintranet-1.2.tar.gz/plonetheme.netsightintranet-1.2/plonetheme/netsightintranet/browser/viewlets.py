from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.layout.viewlets.common import ViewletBase, PersonalBarViewlet, SearchBoxViewlet, ContentActionsViewlet
from plone.app.layout.viewlets.content import DocumentBylineViewlet
from zope.component import getMultiAdapter
from urllib import quote_plus

class IntranetPersonalBarViewlet(PersonalBarViewlet):
    render = ViewPageTemplateFile('templates/personal_bar.pt')

    def update(self):
        self.portal_state = getMultiAdapter((self.context, self.request),
                                            name=u'plone_portal_state')
        PersonalBarViewlet.update(self)

        if not self.anonymous:
            member = self.portal_state.member()
            userid = member.getId()
            self.member_url = self.portal_url + '/Members/' + quote_plus(userid)


class IntranetSearchBoxViewlet(SearchBoxViewlet):
    render = ViewPageTemplateFile('templates/searchbox.pt')

    def update(self):
        self.portal_state = getMultiAdapter((self.context, self.request),
                                            name=u'plone_portal_state')
        SearchBoxViewlet.update(self)


class IntranetDocumentBylineViewlet(DocumentBylineViewlet):
    render = ViewPageTemplateFile('templates/document_byline.pt')

    def update(self):
        self.portal_state = getMultiAdapter((self.context, self.request),
                                            name=u'plone_portal_state')
        DocumentBylineViewlet.update(self)


class IntranetContentActionsViewlet(ContentActionsViewlet):
    render = ViewPageTemplateFile('templates/contentactions.pt')
    
    def update(self):
        self.portal_state = getMultiAdapter((self.context, self.request),
                                            name=u'plone_portal_state')

        ContentActionsViewlet.update(self)
