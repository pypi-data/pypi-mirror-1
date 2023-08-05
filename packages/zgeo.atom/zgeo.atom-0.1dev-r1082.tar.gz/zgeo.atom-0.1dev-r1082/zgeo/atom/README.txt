zgeo.atom Package Readme
=========================

Objects that provide IGeoItem can be represented as Atom entries using this
package's link entry view.

    >>> from zgeo.geographer.interfaces import IGeoItem
    
Let's create geometry and placemark mocks:
    
    >>> from zope.interface import implements, Interface
    >>> from zope.component import provideAdapter
    >>> from zgeo.geographer.interfaces import IGeometry
    >>> from zope.dublincore.interfaces import ICMFDublinCore
    >>> from zope.traversing.browser.interfaces import IAbsoluteURL
    >>> from zope.publisher.interfaces.browser import IBrowserRequest

    >>> class Point(object):
    ...     implements(IGeometry)
    ...     def __init__(self, long, lat):
    ...         self.type = 'Point'
    ...         self.long = long
    ...         self.lat = lat
    ...     @property
    ...     def coordinates(self):
    ...         return (self.long, self.lat)

    >>> class Placemark(object):
    ...     implements((IGeoItem, ICMFDublinCore))
    ...     def __init__(self, id, summary, long, lat):
    ...         self.id = id
    ...         self.properties = {'summary': summary}
    ...         self.geometry = Point(long, lat)
    ...     def absolute_url(self):
    ...         return 'http://example.com/%s' % self.id
    ...     def Title(self):
    ...         return self.id.capitalize()
    ...     def Description(self):
    ...         return self.properties['summary']
    ...     def CreationDate(self):
    ...         return '2007-12-07 12:00:00'
    ...     def ModificationDate(self):
    ...         return '2007-12-07 12:01:00'

We also need a view to provide IAbsoluteURL

    >>> class AbsoluteURL(object):
    ...     def __init__(self, context, request):
    ...         self.context = context
    ...     def __call__(self):
    ...         return self.context.absolute_url()

    >>> provideAdapter(AbsoluteURL, adapts=(Interface, IBrowserRequest), provides=IAbsoluteURL)

Create a placemark instance

    >>> placemark = Placemark('a', "Place marked 'A'", -105.08, 40.59)

Test the view

    >>> from zgeo.atom.browser import LinkEntry
    >>> from zope.publisher.browser import TestRequest
    >>> request = TestRequest()
    >>> view = LinkEntry(placemark, request)
    >>> view # doctest: +ELLIPSIS
    <zgeo.atom.browser.LinkEntry object at ...>
    
    >>> view.id
    'http://example.com/a/@@atom-link-entry'
    >>> view.title
    'A'
    >>> view.summary
    "Place marked 'A'"
    >>> view.published
    '2007-12-07T12:00:00-07:00'
    >>> view.updated
    '2007-12-07T12:01:00-07:00'
    >>> view.alternate_link
    'http://example.com/a'

    >>> view.hasPolygon
    0
    >>> view.hasLineString
    0
    >>> view.hasPoint
    1
    >>> view.coords_georss
    '40.590000 -105.080000'

Test the feed view

    >>> class Collection(dict):
    ...     implements(ICMFDublinCore)
    ...     def absolute_url(self):
    ...         return 'http://example.com/collection'
    ...     def Title(self):
    ...         return 'Test Collection'
    ...     def Description(self):
    ...         return 'A collection for testing'
    ...     def ModificationDate(self):
    ...         return '2007-12-07 12:01:00'
    ...     def __call__(self):
    ...         return 'http://example.com/collection'

    >>> collection = Collection()
    >>> collection['a'] = placemark
    >>> from zgeo.atom.browser import SubscriptionFeed
    >>> view = SubscriptionFeed(collection, request)
    >>> view # doctest: +ELLIPSIS
    <zgeo.atom.browser.SubscriptionFeed object at ...>
    >>> view.title
    'Test Collection'
    >>> view.updated
    '2007-12-07T12:01:00-07:00'
    >>> view.alternate_link
    'http://example.com/collection'
    >>> view.self_link
    'http://example.com/collection/@@atom-feed-subscription'
    >>> view.previous_archive_link
    'None'
    >>> view.entries # doctest: +ELLIPSIS
    <generator object at ...>
    >>> [e for e in view.entries][0] # doctest: +ELLIPSIS
    <zgeo.atom.browser.LinkEntry object at ...>

Test the search view. Any container that is to serve as a spatial index must
provide both IAttributeAnnotatable and ISpatiallyIndexable

    >>> from zope.annotation.interfaces import IAttributeAnnotatable
    >>> from zgeo.spatialindex.interfaces import ISpatiallyIndexable
    >>> from zope.interface import alsoProvides
    >>> alsoProvides(collection, IAttributeAnnotatable)
    >>> alsoProvides(collection, ISpatiallyIndexable)

Register the annotation and index adapters

    >>> from zgeo.spatialindex.index import SpatialIndex
    >>> provideAdapter(SpatialIndex)
    >>> from zope.annotation.attribute import AttributeAnnotations
    >>> from zope.annotation.interfaces import IAnnotations
    >>> provideAdapter(AttributeAnnotations, [IAttributeAnnotatable], IAnnotations)

Index our mock object

    >>> from zgeo.spatialindex.interfaces import ISpatialIndex
    >>> index = ISpatialIndex(collection)
    >>> index.add(('a', (-105.08, 40.59, -105.08, 40.59)))

Test with an empty request

    >>> from zgeo.atom.browser import SearchFeed
    >>> view = SearchFeed(collection, request)
    >>> view # doctest: +ELLIPSIS
    <zgeo.atom.browser.SearchFeed object at ...>
    >>> view.bounds
    >>> view.page
    1
    >>> view.num_pages
    1
    >>> list(view.entries) # doctest: +ELLIPSIS
    [<zgeo.atom.browser.LinkEntry object at ...>]
    >>> view.first_link
    'http://example.com/collection/@@atom-search-feed'
    >>> view.last_link
    'http://example.com/collection/@@atom-search-feed?page=-1'
    >>> view.next_link
    >>> view.previous_link

This request uses a bounding box that misses our mock content and should have
no results

    >>> request = TestRequest(form={'bbox': '0,30,15,45'})
    >>> view = SearchFeed(collection, request)
    >>> view # doctest: +ELLIPSIS
    <zgeo.atom.browser.SearchFeed object at ...>
    >>> view.bounds
    (0.0, 30.0, 15.0, 45.0)
    >>> view.page
    1
    >>> view.num_pages
    0
    >>> list(view.entries) # doctest: +ELLIPSIS
    []

This request uses a bounding box that intersects our mock content and should
have 1 result

    >>> request = TestRequest(form={'bbox': '-115,30,-100,45'})
    >>> view = SearchFeed(collection, request)
    >>> view # doctest: +ELLIPSIS
    <zgeo.atom.browser.SearchFeed object at ...>
    >>> view.bounds
    (-115.0, 30.0, -100.0, 45.0)
    >>> view.page
    1
    >>> view.num_pages
    1
    >>> list(view.entries) # doctest: +ELLIPSIS
    [<zgeo.atom.browser.LinkEntry object at ...>]

Test the "next" document. Should fail since there's only one possible page.

    >>> request = TestRequest(form={'bbox': '-115,30,-100,45', 'page': '2'})
    >>> view = SearchFeed(collection, request) # doctest: +ELLIPSIS
    Traceback (most recent call last):
    ...
    Exception: Page number exceeds number of pages

Test the "last" document. Should succeed.

    >>> request = TestRequest(form={'bbox': '-115,30,-100,45', 'page': '-1'})
    >>> view = SearchFeed(collection, request) # doctest: +ELLIPSIS
    >>> view.page
    -1
    >>> view.num_pages
    1
    >>> list(view.entries) # doctest: +ELLIPSIS
    [<zgeo.atom.browser.LinkEntry object at ...>]

Backing up one previous the last should raise an exception

    >>> request = TestRequest(form={'bbox': '-115,30,-100,45', 'page': '-2'})
    >>> view = SearchFeed(collection, request) # doctest: +ELLIPSIS
    Traceback (most recent call last):
    ...
    Exception: Page number exceeds number of pages

