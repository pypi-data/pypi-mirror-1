from zope.interface import alsoProvides
try:
    from zope.interface import noLongerProvides
except ImportError:
    from Products.Five.utilities.marker import erase as noLongerProvides
    
from zope.component import getAllUtilitiesRegisteredFor
from collective.sectionsubskin.interfaces import ISubskinDefinition

def applyinterface(obj, event):
    """Mark the request with the correct subskin.
    """
    oldroot = event.request.get("subskin_root", None)
    if oldroot is not None:
        event.request.set("subskin_root", None)
        for layer in getAllUtilitiesRegisteredFor(ISubskinDefinition):
            layer = layer.type_interface
            if layer.providedBy(oldroot):
                noLongerProvides(event.request, layer)
            
    for layer in getAllUtilitiesRegisteredFor(ISubskinDefinition):
        layer = layer.type_interface
        if layer.providedBy(obj):
            alsoProvides(event.request, layer)
            try:
                event.request.set("subskin_root", obj) # provide a reference that's visible from TAL
            except TypeError:
                raise # I forget why this block is here, temp. raise instead of pass