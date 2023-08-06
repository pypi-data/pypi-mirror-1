from zope.component import adapts
from zope.interface import implements
from zgeo.atom.interfaces import IAtomMetadata, IWriteAtomMetadata
from zope.annotation.interfaces import IAnnotations, IAnnotatable
from persistent.dict import PersistentDict
import uuid


KEY = 'zgeo.atom.metadata'


class AtomAnnotatableAdapter(object):
    implements(IWriteAtomMetadata)
    adapts(IAnnotatable)

    def __init__(self, context):
        self.context = context
        annotations = IAnnotations(context)
        self.atom = annotations.get(KEY, None)
        if not self.atom:
            annotations[KEY] = PersistentDict()
            self.atom = annotations[KEY]
            self.atom['id'] = None

    def _get_id(self):
        return self.atom['id']

    def _set_id(self, value):
        self.atom['id'] = value

    def setId(self):
        """Set and return a urn:uuid."""
        self.atom['id'] = 'urn:uuid:%s' % str(uuid.uuid4())
        return self.atom['id']

    id = property(_get_id, _set_id)
