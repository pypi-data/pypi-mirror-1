Provides Atom (RFC 4287) entry, subscription feed, and search feed documents
annotated with GeoRSS elements. Implements the Atom Publishing Protocol (RFC
5023).

AtomPub collections can be made of Zope containers using the
"atompub-collection" view. Atom entry representations of contained objects can
be made using the "atom-entry" view. By registering IFileFactory and IWriteFile
adapters, one can allow creation and edit of objects via the Atom Publishing
Protocol.

Major portions of this work were supported by a grant (to Pleiades_) from the
U.S. National Endowment for the Humanities (http://www.neh.gov).

.. _Pleiades: http://atlantides.org/trac/pleiades/wiki

