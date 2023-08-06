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
from zope.component import getMultiAdapter, queryAdapter
import zope.security.proxy

from zgeo.geographer.interfaces import IGeoreferenced
from zgeo.atom.interfaces import IAtomBase, IEntry, ILink
from zgeo.atom.interfaces import IFeed, ISubscriptionFeed, ISearchFeed
from zgeo.atom.interfaces import IWriteAtomMetadata, IAtomPublishable
from zgeo.atom.interfaces import IAtomPubPOSTable
from zgeo.atom.link import Link
import zope.datetime

# zgeo.spatialindex is required to use a bbox parameter with paging search
# feeds
try:
    from zgeo.spatialindex.site import get_catalog
except ImportError:
    def noner(arg):
        return None
    get_catalog = noner

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
    ts = zope.datetime.time(date)
    return zope.datetime.iso8601_date(ts)
    # Convert ISO or RFC 3339 datetime strings to RFC 3339
    # Zope's ZDCAnnotatableAdapter gives RFC 3339. Lose the seconds precision
    #if str(date).find('T') == 10:
    #    s = date.split('.')[0]
    # Plone's AT content types give ISO
    #else:
    #    t = time.strptime(date, '%Y-%m-%d %H:%M:%S')
    #    s =  time.strftime('%Y-%m-%dT%H:%M:%S', t)
    #tz = '%03d:00' % -int(time.timezone/3600)
    #return s + tz

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
        context = zope.security.proxy.removeSecurityProxy(self.context)
        atom = IWriteAtomMetadata(context)
        if atom.id is None:
            return atom.setId()
        return atom.id

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

    @property
    def links(self):
        """Override this."""
        raise NotImplementedError


class LinkEntry(AtomBase):

    implements(IEntry)

    __name__ = 'atom-entry'
    template = NamedTemplate('template-atom-entry')

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.dc = zope.security.proxy.removeSecurityProxy(
            ICMFDublinCore(self.context)
            )
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
    def links(self):
        items = {
            'alternate': Link(
                absoluteURL(self.context, self.request),
                rel='alternate',
                type='text/html')
            }
        if IAtomPublishable.providedBy(self.context):
            items['edit'] = Link(
                "%s/atom-entry" % absoluteURL(self.context, self.request),
                rel='edit',
                type='application/atom+xml;type=entry')
        return items

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
        self.dc = zope.security.proxy.removeSecurityProxy(
            ICMFDublinCore(self.context)
            )

    @property
    def links(self):
        raise NotImplementedError

    @property
    def entries(self):
        context = zope.security.proxy.removeSecurityProxy(self.context)
        for item in context.values():
            yield LinkEntry(item, self.request)

    def collection_href(self):
        if IAtomPubPOSTable.providedBy(self.context):
            return '%s/atompub-collection' % absoluteURL(
                                                self.context, self.request)
        return None


class SubscriptionFeed(FeedBase):

    implements(ISubscriptionFeed)

    __name__ = 'atom-subscription-feed'
    template = NamedTemplate('template-atom-subscription-feed')

    @property
    def links(self):
        return {
            'alternate': Link(
                            absoluteURL(self.context, self.request),
                            rel='alternate',
                            type='text/html'
                            ),
            'self': Link(
                self.request.getURL(),
                rel='self',
                type='application/atom+xml'
                ),
            'previous-archive': Link('None', rel='previous-archive')
            }

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
        self.catalog = None
        self.bounds = None
        self.page = 1
        self.num_results = 0
        self.num_pages = 0
        self.results = []

    def parse_bbox(self, bbox=None):
        if bbox is None:
            b = self.request.form.get('bbox')
            if b is None:
                return None
        else:
            b = bbox
        return tuple(float(x) for x in b.split(','))

    def _first_link(self):
        url = "%s/@@%s" % (
            absoluteURL(self.context, self.request), self.__name__
            )
        if self.bounds:
            url = "%s?bbox=%f,%f,%f,%f" % ((url,) + self.bounds)
        return url

    def _last_link(self):
        url = "%s/@@%s?page=-1" % (
            absoluteURL(self.context, self.request), self.__name__
            )
        if self.bounds:
            url = "%s&bbox=%f,%f,%f,%f" % ((url,) + self.bounds)
        return url

    def _previous_link(self):
        if self.page == 1:
            return 'None'
        url = "%s/@@%s?page=%d" % (
            absoluteURL(self.context, self.request),
            self.__name__,
            self.page - 1
            )
        if self.bounds:
            url = "%s&bbox=%f,%f,%f,%f" % ((url,) + self.bounds)
        return url

    def _next_link(self):
        if self.page == -1 or self.page >= self.num_pages:
            return 'None'
        url = "%s/@@%s?page=%d" % (
            absoluteURL(self.context, self.request),
            self.__name__,
            self.page + 1
            )
        if self.bounds:
            url = "%s&bbox=%f,%f,%f,%f" % ((url,) + self.bounds)
        return url

    def update(self):
        self.bounds = self.parse_bbox()
        if self.bounds is not None:
            self.catalog = get_catalog(self.context)
            if self.catalog is None:
                raise Exception, "Spatial search is not supported in the absence of a spatial catalog"
            results = self.catalog.searchResults(bounds=self.bounds)
            num_results = len(results)
            self.results = results
        else:
            results = list(self.context.values())
            num_results = len(results)
            self.results = results
        
        self.num_pages = num_results/self.page_size + num_results%self.page_size
        self.num_results = num_results
        
        page = int(self.request.form.get('page', 1))
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
        for result in list(self.results)[begin:end]:
            yield LinkEntry(result, self.request)

    @property
    def links(self):
        return {
            'alternate': Link(
                absoluteURL(self.context, self.request),
                rel='alternate',
                type='text/html'
                ),
            'self': Link(
                '%s/@@%s' % (absoluteURL(self.context, self.request), self.__name__),
                rel='self',
                type='application/atom+xml'
                ),
            'first': Link(self._first_link(), rel='first'),
            'last': Link(self._last_link(), rel='last'),
            'previous': Link(self._previous_link(), rel='previous'),
            'next': Link(self._next_link(), rel='next'),
            }

    def __call__(self):
        self.update()
        return self.template().encode('utf-8')


# Named template implementations

entry_template = NamedTemplateImplementation(
    ViewPageTemplateFile('entry.pt')
    )

subscription_feed_template = NamedTemplateImplementation(
    ViewPageTemplateFile('subscription_feed.pt')
    )

search_feed_template = NamedTemplateImplementation(
    ViewPageTemplateFile('search_feed.pt')
    )

