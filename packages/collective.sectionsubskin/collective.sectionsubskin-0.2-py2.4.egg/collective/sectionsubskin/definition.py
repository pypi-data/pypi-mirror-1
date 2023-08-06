from zope.interface import implements, alsoProvides

try:
    from p4a.subtyper import interfaces as stifaces
except:
    stifaces = None

from collective.sectionsubskin.interfaces import ISubskinDefinition

class BaseDefinition(object):
    """The base class for skin definitions."""
    to_implement = (ISubskinDefinition, )

    isSubtype = True

    if stifaces is not None and isSubtype:
        to_implement.append(stifaces.IPortalTypedFolderishDescriptor)
        
    for_portal_type = 'Folder'
    
    implements(*to_implement)
    
    def __init__(self, *args, **kwargs):
        alsoProvides(self, (self.type_interface, ))
        super(BaseDefinition, self).__init__(*args, **kwargs)

    
    def __repr__(self):
        if hasattr(self, "title"):
            return """<SectionSubSkin named %s>""" % (self.title)
        else:
            return """<Broken SectionSubSkin described by %s>""" % (str(self.__dict__))
    
