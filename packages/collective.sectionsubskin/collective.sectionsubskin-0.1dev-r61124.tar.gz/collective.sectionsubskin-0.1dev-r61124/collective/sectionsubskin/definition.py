from zope.interface import implements

try:
    from p4a.subtyper import interfaces as stifaces
except:
    stifaces = None
    
from liberalyouth.themecolouriser import interfaces
from collective.sectionsubskin.interfaces import ISubskinDefinition

class BaseDefinition(object):
    """The base class for skin definitions."""
    to_implement = [ISubskinDefinition]

    isSubtype = True

    if stifaces is not None and isSubtype:
        to_implement.append(stifaces.IPortalTypedFolderishDescriptor)
        
    implements(*to_implement)
    for_portal_type = 'Folder'
    
