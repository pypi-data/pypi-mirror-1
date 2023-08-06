# Zope imports
from zope.interface import implements, Interface
from zope.component import adapts, getMultiAdapter, queryMultiAdapter
from zope.app.publisher.browser import getDefaultViewName
from zope.publisher.interfaces import IPublishTraverse
from zope.publisher.interfaces.http import IHTTPRequest
try:
    from ZPublisher.BaseRequest import DefaultPublishTraverse
    _ZOPE29 = False
except:
    # Allows import in Zope 2.9
    # XXX : This is probably a bad thing
    from zope.app.traversing.adapters import DefaultTraversable as DefaultPublishTraverse
    from Products.ATContentTypes.content.folder import ATFolder
    _ZOPE29 = True


from zope.event import notify
from Products.ATContentTypes.interface import IATFolder
from collective.sectionsubskin.interfaces import ITraverseThroughEvent

class NotifyingTraverser(DefaultPublishTraverse):

    def __init__(self, context, request):
        self.subpath = []
        self.klass = None
        return super(NotifyingTraverser, self).__init__(context, request)


    def publishTraverse(self, request, name):
        # Only intercept certain names...
        notify(TraverseThroughEvent(self.context.aq_inner, request))
        return self.getViewOrTraverse(request, name)

    
    def getViewOrTraverse(self, request, name):
        view = queryMultiAdapter((self.context, request), name=name)
        if view is not None:
            try:
                return view.__of__(self.context)
            except AttributeError:
                return view
        return super(NotifyingTraverser, self).publishTraverse(request, name)
        

if _ZOPE29:
    def _ZOPE29BOBO__bobo_traverse__(self, REQUEST, name):
        """Allows transparent access to session subobjects.
        """
        # sometimes, the request doesn't have a response, e.g. when
        # PageTemplates traverse through the object path, they pass in
        # a phony request (a dict).
        RESPONSE = getattr(REQUEST, 'RESPONSE', None)
        notify(TraverseThroughEvent(self.aq_inner, REQUEST))
        #import pdb ; pdb.set_trace( )
        # Is it a registered sub object
        data = self.getSubObject(name, REQUEST, RESPONSE)
        #import pdb ; pdb.set_trace( )
        if data is not None:
            return data
        
        # Or a standard attribute (maybe acquired...)
        target = None
        method = REQUEST.get('REQUEST_METHOD', 'GET').upper()
        # Logic from "ZPublisher.BaseRequest.BaseRequest.traverse"
        # to check whether this is a browser request
        if (len(REQUEST.get('TraversalRequestNameStack', ())) == 0 and
            not (method in ('GET', 'HEAD', 'POST'))):
            if shasattr(self, name):
                target = getattr(self, name)
        else:
            # We are allowed to acquire
            target = getattr(self, name, None)
        if (target is None):
            # Bring views in

            view = queryMultiAdapter((self, REQUEST), name=name)
            if view is not None:
                target = view
                
        if (target is None and
            method not in ('GET', 'POST') and not
            isinstance(RESPONSE, xmlrpc.Response) and
            REQUEST.maybe_webdav_client):
            return NullResource(self, name, REQUEST).__of__(self)

        # Raise an AttributeError fallback on Five traversal if we didn't need a
        # NullResource.
        raise AttributeError(name)
    
    ATFolder.__bobo_traverse__ = _ZOPE29BOBO__bobo_traverse__

class TraverseThroughEvent(object):
    """An event which gets sent when traversal passes through an object"""
    implements(ITraverseThroughEvent)
    def __init__(self, ob, request):
        self.object = ob
        self.request = request
        super(TraverseThroughEvent, self).__init__(ob, request)