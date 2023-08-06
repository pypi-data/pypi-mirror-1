from zope import component
from zope.interface import implements, Interface
from zope.app.publication.http import HTTPPublication
from zope.app.publication.requestpublicationfactories import HTTPFactory
from zope.publisher.http import HTTPRequest
from zope.publisher.interfaces import NotFound
from zope.publisher.interfaces.http import IHTTPCredentials
from zope.publisher.interfaces.http import IHTTPRequest
from zope.publisher.interfaces.http import IHTTPApplicationRequest
from zope.publisher.interfaces.http import IHTTPPublisher
from zope.app.container.interfaces import IReadContainer
from zope.filerepresentation.interfaces import IFileFactory, IWriteFile
from zope.filerepresentation.interfaces import IWriteDirectory
from zope.traversing.api import getParent
from zgeo.atom.browser import absoluteURL, LinkEntry
from zgeo.atom.interfaces import IAtomEntryNameFactory


class IAtomPubRequestFactory(Interface):
    pass


class IAtomPubRequest(IHTTPRequest):
    pass


class AtomPubRequest(HTTPRequest):
    implements(IHTTPCredentials, IAtomPubRequest, IHTTPApplicationRequest)


class AtomPubPublication(HTTPPublication):
    pass


class AtomPubPublicationFactory(HTTPFactory):
    def __call__(self):
        request_class = component.queryUtility(
            IAtomPubRequestFactory, default=AtomPubRequest
            )
        return request_class, AtomPubPublication


class AtomPubTraverser(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def publishTraverse(self, request, name):
        if name in ['atompub-collection', 'atom-entry']:
            return self.context
        elif IReadContainer.providedBy(self.context):
            item = self.context.get(name)
            if item is not None:
                return item

        # fall back to views
        view = component.queryMultiAdapter((self.context, request), name=name)
        if view is not None:
            return view

        # give up and return a 404 Not Found error page
        raise NotFound(self.context, name, request)


class AtomCollectionPOST(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def POST(self):
        """Add a new item to the container."""
        name = component.queryMultiAdapter(
                    (self.context, self.request),
                    IAtomEntryNameFactory,
                    ).chooseName()
        body = self.request.bodyStream
        factory = component.getAdapter(
            self.context, IFileFactory, 
            name='application/atom+xml;type=entry'
            )
        placemark = factory(name, 'application/atom+xml;type=entry', body)
        self.context[name] = placemark

        response = self.request.response
        response.setStatus(201)
        loc = "%s/atom-entry" % absoluteURL(self.context[name], self.request)
        response.setHeader('Location', loc)
        return LinkEntry(placemark, self.request)()


class AtomMemberPUT(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def PUT(self):
        body = self.request.bodyStream
        adapter = component.getAdapter(
            self.context, IWriteFile, name='application/atom+xml;type=entry'
            )
        adapter.write(body.read())
        self.request.response.setStatus(200)
        return ''


class AtomMemberDELETE(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def DELETE(self):
        parent = getParent(self.context)
        adapter = component.queryAdapter(
            parent, IWriteDirectory,
            name='application/atom+xml;type=entry',
            default=parent
            )
        adapter.__delitem__(self.context.__name__)
        self.request.response.setStatus(200)
        return ''
