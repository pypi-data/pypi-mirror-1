from zope.component import adapts
from zope.interface import implements, alsoProvides
from zope.dublincore.interfaces import ICMFDublinCore
from zope.dublincore.interfaces import IWriteZopeDublinCore, IZopeDublinCore
from zgeo.geographer.interfaces import IGeoreferenceable, IGeoreferenced
from zope.filerepresentation.interfaces import IFileFactory, IWriteFile
from zope.app.folder import Folder
from zope.app.folder.interfaces import IFolder
from zgeo.atom import feedparser
from zgeo.atom.interfaces import IAtomPublishable
from zgeo.atom.publication import IAtomPubRequest
from zgeo.atom.interfaces import IAtomEntryNameFactory
from zgeo.geographer.interfaces import IWriteGeoreferenced
import datetime
import re
import uuid

class Placemark(object):
    implements((IGeoreferenceable, IGeoreferenced, ICMFDublinCore))
    
    def __init__(self, id, summary, long, lat):
        self.id = id
        self.summary = summary
        self.type = 'Point'
        self.coordinates = (long, lat)
    
    def Title(self):
        return self.__name__.capitalize()
    
    def Description(self):
        return self.summary
    
    def CreationDate(self):
        return '2007-12-07 12:00:00'
    
    def ModificationDate(self):
        return '2007-12-07 12:01:00'

class PlacesFolder(Folder):
    implements(ICMFDublinCore)
    
    def Title(self):
        return self.__name__.capitalize()
    
    def Description(self):
        return 'Test Places'
    
    def CreationDate(self):
        return '2007-12-07 12:00:00'
    
    def ModificationDate(self):
        return '2007-12-07 12:01:00'

class AbsoluteURL(object):
    
    def __init__(self, context, request):
        self.context = context
    
    def __call__(self):
        return self.context.absolute_url()

class AtomFileFactory(object):
    """Adapts a generic content object"""
    implements(IFileFactory)
    adapts(IFolder)

    def __init__(self, context):
        self.context = context
    
    def __call__(self, name, content_type, data):
        feed = feedparser.parse(data)
        entry = feed.entries[0]
        title = entry.get('title', u'Untitled')
        summary = entry.get('summary', u'Unsummarized')
        where = entry.where
        p = Folder()
        dc = IWriteZopeDublinCore(p)
        dc.title = title
        dc.description = summary
        dc.creator = u'Grok'
        geo = IWriteGeoreferenced(p)
        geo.setGeoInterface(where['type'], where['coordinates'])
        now = datetime.datetime.now()
        dc.created = now
        p.__name__ = name
        alsoProvides(p, IAtomPublishable)
        return p

class AtomWriteFile(object):    
    implements(IWriteFile)
    adapts(IFolder)
    
    def __init__(self, context):
        self.context = context
    
    def write(self, data):
        dc = IWriteZopeDublinCore(self.context)
        geo = IWriteGeoreferenced(self.context)
        feed = feedparser.parse(data)
        entry = feed.entries[0]
        title = entry.get('title')
        if title is not None:
            dc.title = title
        summary = entry.get('summary')
        if summary is not None:
            dc.description = summary
        where = entry.get('where')
        if where is not None:
            geo.setGeoInterface(where['type'], where['coordinates'])

class AtomEntryNamer(object):
    implements(IAtomEntryNameFactory)
    adapts(IFolder, IAtomPubRequest)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def get_unique_name(self, candidate):
        # Make a unique name from candidate by suffixing
        if candidate not in self.context:
            return candidate
        m = re.search(r"(.+)\.(\d+)$", candidate)
        if not m:
            x = "%s.1" % candidate
        else:
            x = "%s.%d" % (m.groups[0], int(m.groups[1])+1)
        return self.get_unique_name(x)

    def chooseName(self):
        slug = self.request.getHeader('Slug')
        if slug is not None:
            name = slug.strip().lower()
            name = self.get_unique_name(re.sub('\W+', '-', name))
        else:
            name = str(uuid.uuid1())
        return name
