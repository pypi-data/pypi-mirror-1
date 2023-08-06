import unittest
from zope.testing import doctest
from zope.component import provideAdapter
from zope.app.testing.setup import placefulSetUp, placefulTearDown
from zope.app.testing.functional import FunctionalDocFileSuite
from zope.interface import implements, Interface, alsoProvides
from zope.app.intid.interfaces import IIntIds
from zope.app.catalog.interfaces import ICatalog
from zgeo.spatialindex.bounds import Bounded
from zgeo.spatialindex.catalog import Catalog
from zgeo.spatialindex.interfaces import IBounded, ISpatiallyCataloged
from zgeo.atom.example import PlacesFolder, Placemark
from zgeo.atom.testing import AtomLayer
from zgeo.atom.metadata import AtomAnnotatableAdapter
from zope.annotation.attribute import AttributeAnnotations
from zope.annotation.interfaces import IAttributeAnnotatable


optionflags = doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS | doctest.REPORT_ONLY_FIRST_FAILURE

def setUp(test):
    placefulSetUp()
    provideAdapter(Bounded)
    provideAdapter(AttributeAnnotations)
    provideAdapter(AtomAnnotatableAdapter)

    from zope.app.folder import Folder, rootFolder
    root = rootFolder()
    test.globs['root'] = root
    places = PlacesFolder()
    root['places'] = places
    places.__name__ = 'places'
    test.globs['places'] = places

    import os
    os.environ['CLIENT_HOME'] = os.getcwd()

    catalog = Catalog()
    from zope.app.testing import ztapi
    ztapi.provideUtility(ICatalog, catalog)
    from zgeo.spatialindex.index import BoundsIndex
    catalog['bounds'] = BoundsIndex('bounds', IBounded)
    test.globs['catalog'] = catalog

    placemark = Placemark('a', "Place marked 'A'", -105.08, 40.59)
    places['a'] = placemark
    placemark.__parent__ = places
    placemark.__name__ = 'a'
    test.globs['placemark'] = placemark

    catalog.index_doc(1, placemark)
    
    class Ids:
        implements(IIntIds)
        def __init__(self, data):
            self.data = data
        def getObject(self, id):
            return self.data[int(id)]
        def __iter__(self):
            return self.data.iterkeys()
    intids = Ids({1: placemark})
    ztapi.provideUtility(IIntIds, intids)

    alsoProvides(places, ISpatiallyCataloged)
    alsoProvides(places, IAttributeAnnotatable)
    alsoProvides(placemark, IAttributeAnnotatable)

def tearDown(test):
    placefulTearDown()

def test_suite():
    atomdocs = FunctionalDocFileSuite(
            'atom-docs.txt',
            optionflags=optionflags,
            )
    atomdocs.layer = AtomLayer
    atompub = FunctionalDocFileSuite(
            'atom-pub.txt',
            optionflags=optionflags,
            )
    atompub.layer = AtomLayer

    return unittest.TestSuite([
        doctest.DocFileSuite(
            'README.txt',
            package='zgeo.atom',
            setUp=setUp,
            tearDown=tearDown,
            optionflags=optionflags,
            ),
        atomdocs,
        atompub,
        ])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
