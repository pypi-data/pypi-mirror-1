Exporting content
-----------------

To test exporting some content, we'll create content::

    >>> _ = self.folder.invokeFactory("Folder", "content")
    >>> folder = self.folder["content"]
    >>> _ = folder.invokeFactory("Document", "doc1", title="A Document")
    >>> _ = folder.invokeFactory("Document", "doc2", title="A second Document")
    >>> folder.keys()
    ['doc1', 'doc2']

Now we create a ``export context`` -- this will act like a container
holding the exported data.  We'll use the ``TarballExportContext``
here::

    >>> from collective.plone.gsxml.context import TarballExportContext
    >>> export_context = TarballExportContext()

Now we create a exporter object, which will use the export context
created above to store the export data, and use the Marshaller to
actually marshall content.  We initialize the exporter with the
``root`` folder which we want to export::

    >>> from collective.plone.gsxml.content import XMLContentFSExporter
    >>> exporter = XMLContentFSExporter(folder)

Now we're able to start the export.  We supply the **export context**
and a folder *inside the export context* (thus, one export context can
be used multiple times by supplying different root folders).  We also
specify that this is a root-level export::

    >>> exporter.export(export_context, "structure", True)

Ok, that's it.  The archive stream may now be fetched from the export
context::

    >>> archive = export_context.getArchiveStream()
    >>> archive.seek(0)

Importing content
-----------------

To test importing, we'll delete the objects exported above::

    >>> folder.manage_delObjects(['doc1', 'doc2'])
    >>> folder.keys()
    []

Now we create a ``import context``, which will hold our exported
stream, and a importer, which will use that import context to read
marshalled data from::

    >>> from collective.plone.gsxml.context import TarballImportContext
    >>> import_context = TarballImportContext(archive)

The importer -- we initialize the importer with the *target* folder::

    >>> from collective.plone.gsxml.content import XMLContentFSImporter
    >>> importer = XMLContentFSImporter(folder)

Now we start the import. We supply the **import context** and the root
folder *within* the import context.  Also, we indicate that this is
indeed a root-level import::

    >>> importer.import_(import_context, "structure", True)

We're now able to get the documents again::

    >>> folder.keys()
    ['doc1', 'doc2']
    >>> folder.doc1.Title()
    'A Document'

