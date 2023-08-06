from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile
from zope.publisher.interfaces.browser import IBrowserView

from plone.app.kss.plonekssview import PloneKSSView
from plone.app.kss.interfaces import IPloneKSSView

from zope.interface import implements

class Lightboxing(PloneKSSView):
    
    implements(IPloneKSSView)

    macroholder = ZopeTwoPageTemplateFile('templates/macropage.pt')

    def doTest(self, fieldname=None):
        """
        kss testing
        """
        ksscore = self.getCommandSet('core')
        zopecommands = self.getCommandSet('zope')
        plonecommands = self.getCommandSet('plone')

        #ksscore.replaceHTML(
        #    ksscore.getHtmlIdSelector('contentActionMenus'), 
        #    'beeeeeeeee')

        return self.render()

    def getInlinePage(self, url, fromParent=False):
        """
        kss testing
        """
        ksscore = self.getCommandSet('core')

        if not fromParent:
            page = self.context.restrictedTraverse(url)
        else:
            page = self.context.aq_inner.aq_parent.restrictedTraverse(url)
            
        template = page

        if IBrowserView.providedBy(template):
            view = template
            for attr in ('index', 'template', '__call__'):
                template = getattr(view, attr, None)
                if template is not None and hasattr(template, 'macros'):
                    break
            if template is None:
                raise KeyError("Unable to find template for view %s" % url)

        if hasattr(template, 'macros') and template.macros.get('main', None):
            mmacro = template.macros['main']
        else:
            raise KeyError("Cannot find main macro in %s" % url) 
        
        if not fromParent:
            mcontext = self.context
        else:
            mcontext = self.context.aq_inner.aq_parent

        html = self.macroholder(context=mcontext,
                                themacro=mmacro,
                                theview=page)

        ksscore.replaceInnerHTML('#lbContent', html)

        return self.render()
        

