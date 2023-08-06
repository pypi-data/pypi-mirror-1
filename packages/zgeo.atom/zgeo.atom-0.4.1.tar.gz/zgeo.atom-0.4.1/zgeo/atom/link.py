from zope.interface import implements
from zgeo.atom.interfaces import ILink


class Link(object):
    implements(ILink)

    def __init__(self, href, rel=None, type='application/atom+xml'):
        self.href = href
        self.rel = rel
        self.type = type
    
