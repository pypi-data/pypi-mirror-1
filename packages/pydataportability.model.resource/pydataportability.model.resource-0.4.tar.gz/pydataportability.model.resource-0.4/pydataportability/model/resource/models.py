from zope.interface import implements
from interfaces import *
from UserList import UserList
import re

placeholder_pattern = re.compile("{%(.+?)}")

class TemplateError(Exception):
    """exception being raised for templating problems"""
    msg = u"generic template error"
    
    def __init__(self, template, msg = None):
        """initialize the error instance"""
        self.template = template
        if msg is not None:
            self.msg = msg
        
    def __repr__(self):
        return """Template Error on template '%s': %s""" %(self.template, self.msg)
    
    __str__ = __repr__

class URITemplate(object):
    """helper class for rendering URI templates. This is being used for URI template which contain
    placeholders in the form ``{%param}``. You can instantiate a ``URITemplate`` instance and then 
    call it with all necessary parameters to be replaced like so::
    
        >>> t = URITemplate('http://someuri/somepath/?q={%id})
        >>> t(id='mrtopf')
        'http://someuri/somepath/?q=mrtopf'
        """
    
    def __init__(self, template):
        """initialize the ``URITemplate`` instance and store the template"""
        self.template = template
        
    @property
    def placeholders(self):
        """return a list of all the placeholders found inside a template."""
        return set(placeholder_pattern.findall(self.template))
        
        
    def __call__(self, **kwargs):
        """replaces all parameters inside the template and return the resulting string
        
        TODO: implement a faster way maybe with re although the overhead might not make it faster
        in the end if there's a low amount of placeholders"""
        if len(self.placeholders.intersection(set(kwargs.keys())))!=len(self.placeholders):
            raise TemplateError(self.template, u"Cannot resolve template because"
                "there are not enough arguments given. Arguments given: %s, Arguments needed: %s" %(kwargs.keys(), self.placeholders))
                
        s = self.template
        for a,v in kwargs.items():
            s = s.replace("{%%%s}" %a, v)
        return s


class Resource(object):
    """a ressource described by it's metadata and URI"""
    
    implements(IResource)
    
    def __init__(self, subject = None, aliases = [], expires = None, type_=None, links = []):
        """initialize a Resource with all it's basic informatiion.
        
        ``subject`` is a URI, ``alias`` a list of alternative URIs, ``expires`` a datetime object
        describing the expiration time, ``type`` is the type of the Resource and ``links`` is a
        list of ResourceLink objects describing related resources."""
        self.subject = subject
        self.aliases = aliases
        self.expires = expires
        self.type_ = type_
        self.links = ResourceSet(links)
        

class ResourceSet(UserList):
    """a list of ResourceLink objects pointing to other resources."""
    
    implements(IResourceSet)
    
    def __init__(self, links = []):
        """initialize this resource set with a list of ResourceLink items. This resource set
        can then be queried for specific rel values
        """
        UserList.__init__(self, links)
        self._compute_rel_map()
        
        
    # TODO: check if _set_data etc. can be removed because of manual trigger a la commit()
    def _set_data(self, data):
        """setter for data which also trigger rel-map-computation"""
        print "setting"
        self.data = data
        self._compute_rel_map()
        
    def _get_data(self):
        """getter for the data attribute to make it a property"""
        return self.data
        
    def _compute_rel_map(self):
        """compute the rel->[link] mapping"""
        self.rel_links = {}
        for link in self.data:
            for rel in link.rels:
                self.rel_links.setdefault(rel,[]).append(link)
    
    commit = _compute_rel_map
    
    def get_by_rel(self, rel, min_priority=None):
        """return a list of IResourceLink instances filtered by the given rel attribute
        
        If a ``min_priority`` is given only those resources with an equal or higher priority will
        be returned. If a priority of a link is ``None`` then it will count as priority 0
        """
        links = [link for link in self.rel_links.get(rel,[]) 
                    if min_priority is None or link.priority is None or link.priority>=min_priority]
        links.sort(lambda a,b: cmp(b.priority, a.priority))
        return links
        
    def filter(self, rels=None, media_types=None):
        """filters the list of links by relationships and media types. ``rels`` is a list of ``rel``-Attributes
        to filter for or ``None`` if no filtering for this attribute should take place. ``media_types`` is a list
        of media types to filter for or ``None`` if no filtering should take place"""
        results = []
        if rels is not None:
            rels = set(rels)
        if media_types is not None:
            media_types = set(media_types)

        for link in self:
            if ((rels is None or len(set(link.rels).intersection(rels))>0) and
               (media_types is None or len(set(link.media_types).intersection(media_types))>0)):
                results.append(link)
        results.sort(lambda a,b: cmp(b.priority, a.priority))
        return results
                
        
class ResourceLink(object):
    """a link to a resource with additional metadata"""
    
    implements(IResourceLink)
    
    def __init__(self, rels=[], uris=[], templates=[], media_types=[], subject = None, priority = 0):
        """initialize the link to a resource. The parameters are taken from the XRD specification
        and need to be mapped from other representations.
        
        ``rel`` is a list of zero or more rel values (URIs) describing the type of this link.
        ``uris`` is a list of zero or more URIs describing where to find this resource.
        ``templates`` is a list of zero or more URI templates with placeholders as described in the XRD specification.
        templates will be stored as ``URITemplate`` instances.
        ``media_types`` is a list of zero or more media type values describing the contents of the resource.
        ``Subject`` is the subject of the linked resource and must match it.
        ``priority`` is an optional priority value describing the priority of this resource link.
        """
        self.rels = rels
        self.uris = uris
        self.templates = [URITemplate(tmpl) for tmpl in templates]
        self.media_types = media_types
        self.subject = subject
        if priority is None:
            priority = 0
        self.priority = priority
        
    def get(self, uri = None, **tmpl_params):
        """retrieve the resource. If no ``uri`` parameter is given then the first URI in the list
        of URIs for this link will be used. Otherwise the URI given will be used if it's in the list of
        valid URIs. If no ``uri`` parameter is given and some ``tmpl_params`` are given in the form of
        named parameters then the first URI template from the list for this link is taken and the placeholders
        are replaced by the named parameters given."""
        
    def __repr__(self):
        return """ResourceLink for rels %s and uris %s, templates %s""" %(self.rels, self.uris, self.templates)
