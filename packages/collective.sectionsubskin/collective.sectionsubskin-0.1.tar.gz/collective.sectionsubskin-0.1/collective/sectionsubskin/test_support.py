from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from collective.sectionsubskin.browser.subskin import SubSkin
from collective.sectionsubskin.interfaces import ISubskinDefinition
from collective.sectionsubskin.definition import BaseDefinition

class IRedSkin(ISubskinDefinition): 
    pass

class IBlueSkin(ISubskinDefinition): 
    pass


class RedSkin(BaseDefinition):
    
    title = u"RedSkin"
    colour = u"FF0000"
    type_interface = IRedSkin
    

class BlueSkin(BaseDefinition):
    title = u"BlueSkin"
    colour = u"0000FF"
    type_interface = IBlueSkin


class colours(SubSkin):
    """ Colours. """
    
    def render(self):
        """ Render the CSS. """
        try:
            return """html { background-color: #%s; }""" % (self.subskin.colour)
        except:
            return """"""
    
    __call__ = render#ViewPageTemplateFile('css.pt')
