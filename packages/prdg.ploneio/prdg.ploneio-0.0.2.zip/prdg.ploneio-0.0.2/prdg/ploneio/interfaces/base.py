from zope.interface import Interface, Attribute

class IContextAndRequestAware(Interface):
    """
    Something aware of a context and a request.
        
    This will be normally implemented as an adapter to (context, request), 
    like an `IBrowserView` for example.
    """
    
    context = Attribute("""The context.""")
    request = Attribute("""The request.""")    