data collector
==============

For the root exporter we have a data collector which gets passed
through all exporters. There they can set data, and the root exporter
can after the export step write a manifest file for
the export.

Now do the full monty
---------------------

Funky imports::

  >>> from collective.plone.gsxml import collector, content, context

Setup roles and test documents::

  >>> self.setRoles(("Manager",))
  >>> self.folder.invokeFactory("Document", "doc")
  'doc'
  >>> self.folder.invokeFactory("Document", "doc2")
  'doc2'
  >>> self.folder.doc.addReference(self.folder.doc2) # doctest: +ELLIPSIS
  <Reference sid:... tid:... rel:None>

We need to know the UIDs for later::

  >>> doc_uid = self.folder.doc.UID()
  >>> doc2_uid = self.folder.doc2.UID()

For testing porposes, we use a dummy export context which stores inside
a dict::

  >>> ec = context.DummyContext()

Create a collector. This will be passed around and used by the
filesystem exporters to dump data in.::

  >>> coll = collector.SimpleDictCollector()

Create a filesystem exporter. Initialize it with with a context to be exported
and a collector::

  >>> fse = content.XMLContentFSExporter(self.folder, coll)

Get that export going, man! ::

  >>> fse.export(ec, "")

We need to have two objects in the collector brain::

  >>> len( coll.brain.keys() ) == 3
  True

And we have some stuff collected::

  >>> sorted(coll.brain[doc_uid]["files"].keys())
  ['doc.description.data', 'doc.refs.pickle', 'doc.rights.data', 'doc.text.data']

The references are collected::

  >>> refs = coll.brain[doc_uid]["references"]
  >>> len(refs) == 1
  True
  >>> ref = refs.values()[0]
  >>> ref["sourceUID"] == doc_uid
  True
  >>> ref["targetUID"] == doc2_uid
  True

