import zope.publisher.browser
import zope.app.pagetemplate.viewpagetemplatefile

from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

class Macros(zope.publisher.browser.BrowserView):
    template = zope.app.pagetemplate.viewpagetemplatefile.ViewPageTemplateFile(
        'calameomacros.pt')

    def __getitem__(self, key):
        return self.template.macros[key]

class CalameoView(BrowserView):
    """ default calameo PDF view """
    template = ViewPageTemplateFile("calameoview.pt")

    def __call__(self):
        return self.template()
    
    @property
    def calameo_id(self):
        return self.context.calameoid
       
    @property
    def calameo_width(self):
        return self.context.getWidth()
        
    @property
    def calameo_height(self):
        return self.context.getHeight()
        
    