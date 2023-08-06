from zope.interface import alsoProvides
from zope.component import getAllUtilitiesRegisteredFor
from collective.sectionsubskin.interfaces import ISubskinDefinition

def applyinterface(obj, event):
    """Mark the request with the correct subskins.
    """
    for layer in getAllUtilitiesRegisteredFor(ISubskinDefinition):
        layer = layer.type_interface
        if layer.providedBy(obj):
            alsoProvides(event.request, layer)
            try:
                event.request.set("subskin_root", obj) # provide a reference that's visible from TAL
            except TypeError:
                raise # I forget why this block is here, temp. raise instead of pass