import grok

from zope import component
from zope.component.interfaces import ComponentLookupError

from zope.traversing.interfaces import TraversalError
from zope.traversing.namespace import view
from zope.interface import Interface
from zope.interface.interfaces import IInterface
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.publisher.interfaces.http import IHTTPRequest
from zope.app.publication.http import MethodNotAllowed

from grok.interfaces import IRESTSkinType
from zope.publisher.browser import applySkin

class GrokMethodNotAllowed(MethodNotAllowed):
    pass

class MethodNotAllowedView(grok.MultiAdapter):
    grok.adapts(GrokMethodNotAllowed, IHTTPRequest)
    grok.name('index.html')
    grok.implements(Interface)
    
    def __init__(self, error, request):
        self.error = error
        self.request = request
        self.allow = self._getAllow()
        
    def _getAllow(self):
        allow = []
        for method in ['GET', 'PUT', 'POST', 'DELETE']:
            view = component.queryMultiAdapter(
                (self.error.object, self.error.request),
                name=method)
            if view is not None:
                is_not_allowed = getattr(view, 'is_not_allowed', False)
                if not is_not_allowed:
                    allow.append(method)
        allow.sort()
        return allow
    
    def __call__(self):
        self.request.response.setHeader('Allow', ', '.join(self.allow))
        self.request.response.setStatus(405)
        return 'Method Not Allowed'

class rest_skin(view):
    """A rest skin.
    
    This used to be supported by zope.traversing but the change was backed out.
    We need it for our REST support.
    """
    def traverse(self, name, ignored):
        self.request.shiftNameToApplication()
        try:
            skin = component.getUtility(IRESTSkinType, name)
        except ComponentLookupError:
            raise TraversalError("++rest++%s" % name)
        applySkin(self.request, skin)
        return self.context


class NotAllowedREST(grok.REST):
    """These are registered for everything by default to cause the correct
    errors.

    Any more specific REST view overrides this.
    """
    grok.layer(grok.IRESTLayer)
    grok.context(Interface)

    is_not_allowed = True
    
    def GET(self):
        raise GrokMethodNotAllowed(self.context, self.request)
            
    def POST(self):
        raise GrokMethodNotAllowed(self.context, self.request)
            
    def PUT(self):
        raise GrokMethodNotAllowed(self.context, self.request)
    
    def DELETE(self):
        raise GrokMethodNotAllowed(self.context, self.request)
            
