
namespaces = {} 

class Namespace(object):
    def __init__(self, uri, prefix=None):
        self.uri = uri
        self.prefix = prefix
        if prefix:
            namespaces[uri] = prefix
            
    def qname(self, name):
        if self.prefix:
            return self.prefix + ':' + name
        else:
            return name
        
    def clarkname(self, name):
        if self.uri:
            return '{%s}%s' % (self.uri, name)
        else:
            return name
    
    __getattr__ = clarkname
    __getitem__ = clarkname
    
    def __str__(self):
        return self.uri
    def __unicode__(self):
        return unicode(self.uri)
    def __repr__(self):
        return 'Namespace(%r, %r)' % (self.uri, self.prefix)
    def __equals__(self, other):
        if isinstance(other, basestring):
            return self.uri == other
        elif isinstance(other, Namespace):
            return self.uri == other.uri
        else:
            return 0
    
xml = Namespace('http://www.w3.org/XML/1998/namespace', 'xml')
xhtml = Namespace('http://www.w3.org/1999/xhtml', 'html')
atom = Namespace('http://purl.org/atom/ns#', 'atom')
rdf = Namespace('http://www.w3.org/1999/02/22-rdf-syntax-ns#', 'rdf')
rss = Namespace('http://purl.org/rss/1.0/', 'rss')
nons = Namespace(None, None)

__all__ = ['xml', 'xhtml', 'atom', 'rdf', 'rss', 'nons', 'Namespace']
