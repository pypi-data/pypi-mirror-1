from zope.interface import alsoProvides
from zope.component import getAllUtilitiesRegisteredFor
from collective.sectionsubskin.interfaces import ISubskinDefinition

def applyinterface(object, event):
    """Mark the request with the correct subskins.
    """
    for layer in getAllUtilitiesRegisteredFor(ISubskinDefinition):
        layer = layer.type_interface
        if layer.providedBy(object):
            alsoProvides(event.request, layer)
            try:
                event.request.set("subskin_root", object)
            except:
                pass