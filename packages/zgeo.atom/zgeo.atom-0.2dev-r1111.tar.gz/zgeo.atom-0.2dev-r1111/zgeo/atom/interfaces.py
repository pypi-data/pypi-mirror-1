
from zope.interface import Interface, Attribute


class IAtomBase(Interface):
    
    """See http://tools.ietf.org/html/rfc4287.
    """

    author = Attribute("""A mapping with name, URI, and email keys""")
    id = Attribute("""A universally unique identifier""")
    title = Attribute("""A human readable text""")
    updated = Attribute("""A RFC 3339 date/time string""")


class IEntry(IAtomBase):

    """See http://tools.ietf.org/html/rfc4287.
    """

    alternate_link = Attribute("""URL of the resource linked by the entry""")
    summary = Attribute("""A human readable text summary""")
    updated = Attribute("""A RFC 3339 date/time string""")

    # geographic elements
    coords_georss = Attribute("""GML coordinate encoding of the location""")
    hasLineString = Attribute("""Boolean, True if has a line location""")
    hasPoint = Attribute("""Boolean, True if has a point location""")
    hasPolygon = Attribute("""Boolean, True if has a polygon location""")


class IFeed(IAtomBase):

    """See http://tools.ietf.org/html/rfc4287.
    """

    entries = Attribute("""An iterator over feed entries""")
    alternate_link = Attribute("""URL of the context resource""")
    self_link = Attribute("""The feed's own preferred URL""")


class ISubscriptionFeed(IFeed):

    """See http://tools.ietf.org/html/rfc5005.
    """
    
    previous_archive_link = Attribute("""URI of the immediately preceeding document""")


class IArchiveFeed(IFeed):

    """See http://tools.ietf.org/html/rfc5005.
    """

    current_link = Attribute("""URI of the subscription document""")
    next_archive_link = Attribute("""URI of the immediately following document""")
    previous_archive_link = Attribute("""URI of the immediately preceding document""")


class IPagingFeed(IFeed):

    """See http://tools.ietf.org/html/rfc5005.
    """

    first_link = Attribute("""URI of the furthest preceding document""")
    last_link = Attribute("""URI of the furthest following document""")
    previous_link = Attribute("""URI of the immediately preceding document""")
    next_link = Attribute("""URI of the immediately following document""")


class ISearchFeed(IPagingFeed):

    bounds = Attribute("""A (minx, miny, maxx, maxy) tuple""")
    page = Attribute("""Integer page number""")

