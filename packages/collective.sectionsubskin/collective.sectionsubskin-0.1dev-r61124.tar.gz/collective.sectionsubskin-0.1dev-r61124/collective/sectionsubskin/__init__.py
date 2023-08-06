"""from Products.ATContentTypes.content.folder import ATFolder
import ZPublisher.BaseRequest
from monkey import wrap

@wrap(ZPublisher.BaseRequest.DefaultPublishTraverse.publishTraverse, 'f178b97f0c98014585a0b2d926f0dde50920cf3e')
def publishTraverse(func, *args):
    " Traverse. "
    from zope.event import notify
    from zope.app.publication.interfaces import BeforeTraverseEvent
    notify(BeforeTraverseEvent(args[0], args[2]))
    func(*args)

 
ATFolder.publishTraverse = publishTraverse
"""