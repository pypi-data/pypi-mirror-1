zgeo.atom Package Readme
=========================

Test setting atom:id through the AtomMetadata annotator

    >>> from zgeo.atom.interfaces import IWriteAtomMetadata
    >>> atom = IWriteAtomMetadata(places)
    >>> atom.id = 'urn:uuid:places'
    >>> atom.id
    'urn:uuid:places'
    >>> atom = IWriteAtomMetadata(placemark)
    >>> atom.id = 'urn:uuid:placemark'
    >>> atom.id
    'urn:uuid:placemark'

Objects that provide IGeoItem can be represented as Atom entries using this
package's link entry view.

Test the Atom link entry view of the placemark

    >>> from zgeo.atom.browser import LinkEntry
    >>> from zope.publisher.browser import TestRequest
    >>> request = TestRequest()
    >>> view = LinkEntry(placemark, request)
    >>> view
    <zgeo.atom.browser.LinkEntry object at ...>
    
    >>> view.id
    'urn:uuid:placemark'
    >>> view.title
    'A'
    >>> view.summary
    "Place marked 'A'"
    >>> view.published
    '2007-12-07T19:00:00Z'
    >>> view.updated
    '2007-12-07T19:01:00Z'
    >>> [(x.href, x.rel, x.type) for x in view.links.values()]
    [('http://127.0.0.1/places/a', 'alternate', 'text/html')]

    >>> view.hasPolygon
    0
    >>> view.hasLineString
    0
    >>> view.hasPoint
    1
    >>> view.coords_georss
    '40.590000 -105.080000'

Test the feed view

    >>> from zgeo.atom.browser import SubscriptionFeed
    >>> view = SubscriptionFeed(places, request)
    >>> view
    <zgeo.atom.browser.SubscriptionFeed object at ...>
    >>> view.title
    'Places'
    >>> view.updated
    '2007-12-07T19:01:00Z'
    >>> [(x.href, x.rel, x.type) for x in view.links.values()]
    [('http://127.0.0.1', 'self', 'application/atom+xml'), ('http://127.0.0.1/places', 'alternate', 'text/html'), ('None', 'previous-archive', 'application/atom+xml')]
    >>> view.entries
    <generator object at ...>
    >>> [e for e in view.entries][0]
    <zgeo.atom.browser.LinkEntry object at ...>

Test the search view. Any container that is to serve as a spatial index must
provide both IAttributeAnnotatable and ISpatiallyIndexable. This is done in the test setup.


Test with an empty request

    >>> from zgeo.atom.browser import SearchFeed
    >>> view = SearchFeed(places, request)
    >>> view
    <zgeo.atom.browser.SearchFeed object at ...>
    >>> view.update()
    >>> view.bounds
    >>> view.page
    1
    >>> view.num_pages
    1
    >>> list(view.entries)
    [<zgeo.atom.browser.LinkEntry object at ...>]
    >>> [(x.href, x.rel, x.type) for x in view.links.values()]
    [('http://127.0.0.1/places/@@atom-search-feed?page=-1', 'last', 'application/atom+xml'), ('http://127.0.0.1/places/@@atom-search-feed', 'self', 'application/atom+xml'), ('http://127.0.0.1/places', 'alternate', 'text/html'), ('None', 'next', 'application/atom+xml'), ('http://127.0.0.1/places/@@atom-search-feed', 'first', 'application/atom+xml'), ('None', 'previous', 'application/atom+xml')]

This request uses a bounding box that misses our mock content and should have
no results.

    >>> request = TestRequest(form={'bbox': '0,30,15,45'})
    >>> view = SearchFeed(places, request)
    >>> view
    <zgeo.atom.browser.SearchFeed object at ...>
    >>> view.update()
    >>> view.bounds
    (0.0, 30.0, 15.0, 45.0)
    >>> view.page
    1
    >>> view.num_pages
    0
    >>> list(view.entries)
    []

This request uses a bounding box that intersects our mock content and should
have 1 result

    >>> request = TestRequest(form={'bbox': '-115,30,-100,45'})
    >>> view = SearchFeed(places, request)
    >>> view
    <zgeo.atom.browser.SearchFeed object at ...>
    >>> view.update()
    >>> view.bounds
    (-115.0, 30.0, -100.0, 45.0)
    >>> view.page
    1
    >>> view.num_results
    1
    >>> view.num_pages
    1
    >>> list(view.entries)
    [<zgeo.atom.browser.LinkEntry object at ...>]
    >>> entry = list(view.entries)[0]
    >>> entry.id
    'urn:uuid:placemark'
    >>> entry.title
    'A'
    >>> entry.summary
    "Place marked 'A'"
    >>> entry.published
    '2007-12-07T19:00:00Z'
    >>> entry.updated
    '2007-12-07T19:01:00Z'
    >>> [(x.href, x.rel, x.type) for x in view.links.values()]
    [('http://127.0.0.1/places/@@atom-search-feed?page=-1&bbox=-115.000000,30.000000,-100.000000,45.000000', 'last', 'application/atom+xml'), ('http://127.0.0.1/places/@@atom-search-feed', 'self', 'application/atom+xml'), ('http://127.0.0.1/places', 'alternate', 'text/html'), ('None', 'next', 'application/atom+xml'), ('http://127.0.0.1/places/@@atom-search-feed?bbox=-115.000000,30.000000,-100.000000,45.000000', 'first', 'application/atom+xml'), ('None', 'previous', 'application/atom+xml')]

Test the "next" document. Should fail since there's only one possible page.

    >>> request = TestRequest(form={'bbox': '-115,30,-100,45', 'page': '2'})
    >>> view = SearchFeed(places, request)
    >>> view.update()
    Traceback (most recent call last):
    ...
    Exception: Page number exceeds number of pages

Test the "last" document. Should succeed.

    >>> request = TestRequest(form={'bbox': '-115,30,-100,45', 'page': '-1'})
    >>> view = SearchFeed(places, request)
    >>> view.update()
    >>> view.page
    -1
    >>> view.num_pages
    1
    >>> list(view.entries)
    [<zgeo.atom.browser.LinkEntry object at ...>]

Backing up one previous the last should raise an exception

    >>> request = TestRequest(form={'bbox': '-115,30,-100,45', 'page': '-2'})
    >>> view = SearchFeed(places, request)
    >>> view.update()
    Traceback (most recent call last):
    ...
    Exception: Page number exceeds number of pages

