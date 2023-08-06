from zope.app.content import interfaces as contentifaces
from zope.interface import alsoProvides
from zope.component.interfaces import IObjectEvent
try:
    from p4a.subtyper.interfaces import IPortalTypedFolderishDescriptor
except:
    from zope.interface import Interface as IPortalTypedFolderishDescriptor
    
class ISubskinDefinition(IPortalTypedFolderishDescriptor):
    """Defines one of the possible subskins."""
    pass



class ITraverseThroughEvent(IObjectEvent):
    """An event which gets sent when traversal passes through an object"""
    pass

alsoProvides(ISubskinDefinition, contentifaces.IContentType)
