from zope.app.content import interfaces as contentifaces
from zope.interface import alsoProvides, Attribute

try:
    # Use Zope 3.3
    from zope.component.interfaces import IObjectEvent
except:
    # Fall back to 3.2
    from zope.app.event.interfaces import IObjectEvent

try:
    # Load P4A Subtyper if available
    from p4a.subtyper.interfaces import IPortalTypedFolderishDescriptor
except:
    # Use interface.Interface as a dummy if not
    from zope.interface import Interface as IPortalTypedFolderishDescriptor
    
class ISubskinDefinition(IPortalTypedFolderishDescriptor):
    """Defines one of the possible subskins."""
    pass
    #title = Attribute('Contents of the file.')


class ITraverseThroughEvent(IObjectEvent):
    """An event which gets sent when traversal passes through an object"""
    pass

alsoProvides(ISubskinDefinition, contentifaces.IContentType)
