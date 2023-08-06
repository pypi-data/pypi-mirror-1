# Zope imports
from zope.interface import implements, Interface
from zope.component import adapts, getMultiAdapter, queryMultiAdapter
from zope.app.publisher.browser import getDefaultViewName
from zope.publisher.interfaces import IPublishTraverse
from zope.publisher.interfaces.http import IHTTPRequest
from ZPublisher.BaseRequest import DefaultPublishTraverse

from zope.event import notify
from Products.ATContentTypes.interface import IATFolder
from collective.sectionsubskin.interfaces import ITraverseThroughEvent

class NotifyingTraverser(DefaultPublishTraverse):

    adapts(IATFolder, IHTTPRequest)
    
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
            return view.__of__(self.context)
        return super(NotifyingTraverser, self).publishTraverse(request, name)


class TraverseThroughEvent(object):
    """An event which gets sent when traversal passes through an object"""
    implements(ITraverseThroughEvent)
    def __init__(self, ob, request):
        self.object = ob
        self.request = request
        super(TraverseThroughEvent, self).__init__(ob, request)