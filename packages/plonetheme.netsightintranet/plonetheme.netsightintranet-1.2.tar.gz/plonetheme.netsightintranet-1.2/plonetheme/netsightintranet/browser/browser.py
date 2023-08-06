from Products.Five import BrowserView
from plone.app.kss.plonekssview import PloneKSSView
from plone.app.kss.interfaces import IPloneKSSView

from zope.interface import implements

class IntranetDocumentView(BrowserView):
   pass

class ToggleEditToolbar(PloneKSSView):

    implements(IPloneKSSView)

    def __call__(self):
        request = self.request
        referrer = request.get('HTTP_REFERER', '')
        
        if request.get('edit_mode', ''):
            request.RESPONSE.expireCookie('edit_mode', path='/')
        else:
            request.RESPONSE.setCookie('edit_mode', 1, path='/')
        
        if request.get('noRedirect', ''):
            return self.render()
        else:
            return request.RESPONSE.redirect(referrer)

class DummyBrowserView(BrowserView):
   pass


