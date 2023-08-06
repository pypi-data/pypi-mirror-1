from Acquisition import aq_base, aq_inner, aq_parent
from zope.component import getMultiAdapter, queryMultiAdapter
from plone.memoize.instance import memoize

from plone.app.content.browser.folderfactories import FolderFactoriesView

class NetsightFolderFactoriesView(FolderFactoriesView):
    @memoize
    def add_context(self):
        """ plone's context_state.folder doesn't work properly """
        context_state = getMultiAdapter((self.context, self.request), name='plone_context_state')

        if context_state.is_structural_folder(): # and not context_state.is_default_page():
            return aq_inner(context_state.context)
        else:
            return context_state.parent()
