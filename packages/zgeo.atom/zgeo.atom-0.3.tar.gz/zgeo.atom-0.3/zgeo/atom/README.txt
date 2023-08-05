zgeo.atom Package Readme
=========================

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
    'http://127.0.0.1/places/a/@@atom-link-entry'
    >>> view.title
    'A'
    >>> view.summary
    "Place marked 'A'"
    >>> view.published
    '2007-12-07T12:00:00-07:00'
    >>> view.updated
    '2007-12-07T12:01:00-07:00'
    >>> view.alternate_link
    'http://127.0.0.1/places/a'

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
    '2007-12-07T12:01:00-07:00'
    >>> view.alternate_link
    'http://127.0.0.1/places'
    >>> view.self_link
    'http://127.0.0.1/places/@@atom-feed-subscription'
    >>> view.previous_archive_link
    'None'
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
    >>> view.first_link
    'http://127.0.0.1/places/@@atom-search-feed'
    >>> view.last_link
    'http://127.0.0.1/places/@@atom-search-feed?page=-1'
    >>> view.next_link
    >>> view.previous_link

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
    'http://127.0.0.1/places/a/@@atom-link-entry'
    >>> entry.title
    'A'
    >>> entry.summary
    "Place marked 'A'"
    >>> entry.published
    '2007-12-07T12:00:00-07:00'
    >>> entry.updated
    '2007-12-07T12:01:00-07:00'
    >>> entry.alternate_link
    'http://127.0.0.1/places/a'

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

