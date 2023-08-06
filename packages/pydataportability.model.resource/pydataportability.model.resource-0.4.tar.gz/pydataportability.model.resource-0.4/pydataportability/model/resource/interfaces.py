from zope.interface import Interface, Attribute

class IResource(Interface):
    """describes a resource"""
    
    subject = Attribute("""Provides the canonical identifier for the resource""")
    aliases = Attribute("""Provides additional identifiers for the resoure""")
    expires = Attribute("""Specifies when this resource description expires""")
    type_ = Attribute("""Declares a property of the resource""")
    
    
    links = Attribute("""an IResourceSet instance describing related resources""")
    
        
class IResourceSet(Interface):
    """a list of resources, usually IResourceLink items retrieved via ``<Link>`` elements from an XRD document"""
    
    def get_by_rel(rel, min_priority=None):
        """return a list of IResourceLink instances filtered by the given rel attribute
        
        If a ``min_priority`` is given only those resources with an equal or higher priority will
        be returned
        """
    
class IResourceLink(Interface):
    """a link to another resources"""
    
    rels = Attribute("""list of relationships for this service (zero or more)""")
    uris = Attribute("""zero or more URIs idenifying the linked resource""")
    uri_templates = Attribute("""zero or more URI templates idenifying the linked resource""")
    media_types = Attribute("""one or more media types the linked resource can be retrieved as""")
    priority = Attribute("""an optional priority for this link""")
    
    def get(uri = None, **tmpl_params):
        """retrieve the linked resource, returns a new IResource instance.
        
        If a URI is given this will be used. If none is given then any URI in the description will
        be used. The given URI must be in the list of allowed URI templates.
        
        If a URI template is given then ``tmpl_params`` must contain those parameters needed to 
        fill in all the template parameters of the template.
        
        """
        
        
