try:
    from zope.publisher.browser import BrowserPage
except:
    from Products.Five.browser import BrowserView as BrowserPage

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from zope.component import getAllUtilitiesRegisteredFor
from collective.sectionsubskin.interfaces import ISubskinDefinition

class SubSkin(BrowserPage):
    
    def __init__(self, context, request):
        self.context=context
        self.request=request
        self.subskin = None
        for layer in getAllUtilitiesRegisteredFor(ISubskinDefinition):
            if layer.type_interface.providedBy(request):
                self.subskin = layer
        

