"""
$Id: $
"""

from zope import interface
from zope.publisher.interfaces import NotFound
from zope.location import ILocation
from zope.security.proxy import removeSecurityProxy

from z3c.traverser import interfaces

class CollectionTraverserTemplate(object):
    """A traverser that knows how to look up objects by sqlalchemy collections """

    interface.implements(interfaces.ITraverserPlugin)

    collection_attributes = ()
    
    def __init__(self, container, request):
        self.context = container
        self.request = request

    def publishTraverse(self, request, name):
        """See zope.publisher.interfaces.IPublishTraverse"""
        if name in self.collection_attributes:
            container = getattr( self.context, name )
            if ILocation.providedBy( container ):
                trusted_ctx = removeSecurityProxy( container )
                trusted_ctx.__parent__ = self.context
                trusted_ctx.__name__   = name
            return container
        raise NotFound( self.context, name, request)
        
def CollectionTraverser( *names ):
    return type( "CollectionsTraverser", (CollectionTraverserTemplate, ), { 'collection_attributes': names} )

