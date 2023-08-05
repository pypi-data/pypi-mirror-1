
from zope.interface import implements
from zope.dublincore.interfaces import ICMFDublinCore
from zgeo.geographer.interfaces import IGeoreferenceable, IGeoreferenced
from zope.app.folder import Folder

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

