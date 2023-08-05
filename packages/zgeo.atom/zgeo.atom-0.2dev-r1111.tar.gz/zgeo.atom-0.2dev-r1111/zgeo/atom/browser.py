
import time

from zope.traversing.browser.interfaces import IAbsoluteURL
from zope.dublincore.interfaces import ICMFDublinCore

try:
    from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
    raise Exception, "Five's ViewPageTemplateFile doesn't work with named templating"
except:
    from zope.app.pagetemplate import ViewPageTemplateFile

from zope.interface import implements
from zope.publisher.browser import BrowserPage
from zope.formlib.namedtemplate import NamedTemplate
from zope.formlib.namedtemplate import NamedTemplateImplementation
from zope.component import getMultiAdapter

from zgeo.geographer.interfaces import IGeoreferenced
from zgeo.atom.interfaces import IAtomBase, IEntry
from zgeo.atom.interfaces import IFeed, ISubscriptionFeed, ISearchFeed

# zgeo.spatialindex is required to use a bbox parameter with paging search
# feeds
try:
    from zgeo.spatialindex.interfaces import ISpatialIndex
except ImportError:
    pass

def coords_to_georss(geom):
    gtype = geom.type
    if gtype == 'Point':
        coords = (geom.coordinates,)
    elif gtype == 'Polygon':
        coords = geom.coordinates[0]
    else:
        coords = geom.coordinates
    tuples = ('%f %f' % (c[1], c[0]) for c in coords)
    return ' '.join(tuples)

def rfc3339(date):
    # Convert ISO or RFC 3339 datetime strings to RFC 3339
    # Zope's ZDCAnnotatableAdapter gives RFC 3339. Lose the seconds precision
    if str(date).find('T') == 10:
        s = date.split('.')[0]
    # Plone's AT content types give ISO
    else:
        t = time.strptime(date, '%Y-%m-%d %H:%M:%S')
        s =  time.strftime('%Y-%m-%dT%H:%M:%S', t)
    tz = '%03d:00' % -int(time.timezone/3600)
    return s + tz

def absoluteURL(ob, request):
    return getMultiAdapter((ob, request), IAbsoluteURL)()


class NullGeometry(object):
    type = None
    coordinates = None


class NullGeoItem(object):
    id = None
    properties = None

    def __init__(self):
        self.geometry = NullGeometry()


class AtomBase(BrowserPage):

    """Not to be instantiated.
    """
    implements(IAtomBase)

    @property
    def id(self):
        return '%s/@@%s' % (absoluteURL(self.context, self.request), self.__name__)

    @property
    def title(self):
        return self.dc.Title()

    @property
    def updated(self):
        return rfc3339(self.dc.ModificationDate())


    @property
    def author(self):
        return {
            'name': self.dc.Creator()
,
            'uri': '',
            'email': ''
            }

    
class LinkEntry(AtomBase):

    implements(IEntry)

    __name__ = 'atom-link-entry'
    template = NamedTemplate('template-atom-link-entry')

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.dc = ICMFDublinCore(self.context)
        try:
            self.geom = IGeoreferenced(self.context)
        except:
            self.geom = NullGeometry()

    @property
    def published(self):
        return rfc3339(self.dc.CreationDate())


    @property
    def summary(self):
        return self.dc.Description()

    @property
    def alternate_link(self):
        return absoluteURL(self.context, self.request)

    @property
    def hasPoint(self):
        return int(self.geom.type == 'Point')

    @property
    def hasLineString(self):
        return int(self.geom.type == 'LineString')

    @property
    def hasPolygon(self):
        return int(self.geom.type == 'Polygon')

    @property
    def coords_georss(self):
        return coords_to_georss(self.geom)

    def __call__(self):
        return self.template().encode('utf-8')


class FeedBase(AtomBase):

    implements(IFeed)

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.dc = ICMFDublinCore(self.context)

    @property
    def alternate_link(self):
        return absoluteURL(self.context, self.request)

    @property
    def self_link(self):
        return '%s/@@%s' \
        % (absoluteURL(self.context, self.request), self.__name__)

    @property
    def entries(self):
        for item in self.context.values():
            yield LinkEntry(item, self.request)


class SubscriptionFeed(FeedBase):

    implements(ISubscriptionFeed)

    __name__ = 'atom-feed-subscription'
    template = NamedTemplate('template-atom-subscription-feed')

    @property
    def previous_archive_link(self):
        return 'None' 

    def __call__(self):
        return self.template().encode('utf-8')


class SearchFeed(FeedBase):

    implements(ISearchFeed)

    __name__ = 'atom-search-feed'
    template = NamedTemplate('template-atom-search-feed')
    page_size = 20

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.dc = ICMFDublinCore(self.context)

        # search parameters
        bbox = request.form.get('bbox')
        if bbox:
            self.bounds = tuple(float(x) for x in bbox.split(','))
        else:
            self.bounds = None

        # Make a spatial search
        if self.bounds:
            try:
                index = ISpatialIndex(self.context)
                self._results = list(index.intersects(self.bounds))
            except:
                raise Exception, "Spatial search is not supported in the absence of a spatial index"
        else:
            self._results = [(key, ()) for key in self.context.keys()]
        num_results = len(self._results)
        self.num_pages = num_results/self.page_size + num_results%self.page_size
        self.num_results = num_results

        page = int(request.form.get('page', 1))
        if page > 1 and page > self.num_pages:
            raise Exception, "Page number exceeds number of pages"
        elif page < 0 and -page > self.num_pages:
            raise Exception, "Page number exceeds number of pages"
        else:
            self.page = page

    @property
    def entries(self):
        if self.page >= 0:
            begin = (self.page-1) * self.page_size
            end = begin + self.page_size
        else:
            begin = self.num_results + (self.page * self.page_size)
            end = begin + self.page_size
        if end > self.num_results: end = self.num_results
        for result in self._results[begin:end]:
            item = self.context[result[0]]
            yield LinkEntry(item, self.request)

    @property
    def first_link(self):
        url = "%s/@@%s" % (
            absoluteURL(self.context, self.request), self.__name__
            )
        if self.bounds:
            url = "%s?bbox=%f,%f,%f,%f" % ((url,) + self.bounds)
        return url

    @property
    def last_link(self):
        url = "%s/@@%s?page=-1" % (
            absoluteURL(self.context, self.request), self.__name__
            )
        if self.bounds:
            url = "%s&bbox=%f,%f,%f,%f" % ((url,) + self.bounds)
        return url

    @property
    def previous_link(self):
        if self.page == 1:
            return None
        url = "%s/@@%s?page=%d" % (
            absoluteURL(self.context, self.request),
            self.__name__,
            self.page - 1
            )
        if self.bounds:
            url = "%s&bbox=%f,%f,%f,%f" % ((url,) + self.bounds)
        return url

    @property
    def next_link(self):
        if self.page == -1 or self.page >= self.num_pages:
            return None
        url = "%s/@@%s?page=%d" % (
            absoluteURL(self.context, self.request),
            self.__name__,
            self.page + 1
            )
        if self.bounds:
            url = "%s&bbox=%f,%f,%f,%f" % ((url,) + self.bounds)
        return url

    def __call__(self):
        return self.template().encode('utf-8')


# Named template implementations

link_entry_template = NamedTemplateImplementation(
    ViewPageTemplateFile('link_entry.pt')
    )

subscription_feed_template = NamedTemplateImplementation(
    ViewPageTemplateFile('subscription_feed.pt')
    )

search_feed_template = NamedTemplateImplementation(
    ViewPageTemplateFile('search_feed.pt')
    )

