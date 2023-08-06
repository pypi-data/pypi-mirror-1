# -*- coding: utf-8 -*-
#
# File: content.py
#
# Copyright (c) InQuant GmbH
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

__author__    = """Ramon Bartl <ramon.bartl@inquant.de>"""
__docformat__ = 'plaintext'
__revision__  = "$Revision: 66927 $"
__version__   = '$Revision: 66927 $'[11:-2]

import os
import logging
from StringIO import StringIO
import pickle

import exceptions

from zope import component
from zope.interface import implements

from Acquisition import aq_base
from OFS.Image import File
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import _createObjectByType
from Products.Archetypes.interfaces import IBaseFolder
from Products.Archetypes.public import FileField, TextField
from Products.Archetypes.utils import getRelURL
from Products.Marshall.registry import getComponent

from collective.plone.gsxml.interfaces import ITypeMapper
from collective.plone.gsxml.interfaces import IXMLMarshaller
from collective.plone.gsxml.interfaces import IXMLDemarshaller
from collective.plone.gsxml.interfaces import IFilesystemExporter
from collective.plone.gsxml.interfaces import IFilesystemImporter
from collective.plone.gsxml.interfaces import IExportXMLMorpher, IImportXMLMorpher

from collective.plone.gsxml import manifest, collector, config, utils

LOGGER="gsxml.content"

def info(msg):
    logging.getLogger(LOGGER).info(msg)

def debug(msg):
    logging.getLogger(LOGGER).debug(msg)

def error(msg):
    logging.getLogger(LOGGER).error(msg)

MANIFEST= "MANIFEST.XML"

def check_for_filefield(field):
    return isinstance(field, FileField) or (isinstance(field, TextField) and config.EXPORT_TEXT_AS_FILE)

#
#   setup_tool handlers
#
def exportSiteStructure(context):
    IFilesystemExporter(context.getSite()).export(context, 'structure', True)

def importSiteStructure(context):
    IFilesystemImporter(context.getSite()).import_(context, 'structure', True)

class GSXMLImportError(exceptions.RuntimeError):
    pass


def remove_uid_namespace(marshaller):
    # mess with marshaller internals, because the interface does
    # not allow us to ignore stuff.

    # Marshaller is horribly broken

    for ns in marshaller.namespaces:
        if ns.prefix is None:
            # Archetypes
            if "uid" in ns.at_fields.keys():
                info("********** REMOVED UID NAMESPACE FROM MARSHALLER")
                del ns.at_fields["uid"]
                return True
    return False

def add_uid_namespace(marshaller):
    # mess with marshaller internals, because the interface does
    # not allow us to ignore stuff.

    # Marshaller is horribly broken

    for ns in marshaller.namespaces:
        if ns.prefix is None:
            # Archetypes
            if "uid" not in ns.at_fields.keys():
                info("********** ADDED UID NAMESPACE TO MARSHALLER")
                from Products.Marshall.namespaces.atns import ArchetypeUID
                uid_attribute  = ArchetypeUID('uid')
                uid_attribute.setNamespace(ns)
                ns.at_fields["uid"] = uid_attribute

class ATCTXMLMarshaller(object):
    """ Marshalls ATContentType -> XML
    """
    implements(IXMLMarshaller)

    def __init__(self, context):
        debug("ATCTXMLMarshaller.__init__: context=%s" % (context.__class__))
        self.context = context
        self.marshaller = getComponent("atxml")
        self.options = {}
        self.morpher = component.queryUtility(IExportXMLMorpher, default=lambda x: x)

    def getxml(self):
        debug("ATCTXMLMarshaller.getxml")
        removed = False
        try:
            if self.options.get("ignore_uid", False):
                removed = remove_uid_namespace(self.marshaller)

            content_type, length, data = self.marshaller.marshall(self.context, **self.options)

            self._xml = data
            self._content_type = content_type
            self._length = length
            return self.morpher(self._xml)
        finally:
            if removed:
                add_uid_namespace(self.marshaller)

    xml = property(getxml, "Property of 'xml'")


class ATCTXMLDemarshaller(object):
    """ Demarshalls XML -> ATContentType
    """
    implements( IXMLDemarshaller )

    def __init__(self, context):
        debug("ATCTXMLDemarshaller.__init__: context=%s" % (context))
        self.context = context
        self.marshaller = getComponent("atxml")
        self.options = {}
        self.typemapper = component.queryUtility(ITypeMapper, default=lambda x: x)
        self.morpher = component.queryUtility(IImportXMLMorpher, default=lambda x: x)

        # or maybe even: self.morpher = IImportXMLMorpher(context, lambda x: x)

    def demarshall(self, instance, xml):
        debug("ATCTXMLDemarshaller.demarshall: instance=%s" % (instance))
        removed = False
        try:
            xml =self.morpher(xml)
            if self.options.get("ignore_uid", False):
                removed = remove_uid_namespace(self.marshaller)
            self.marshaller.demarshall(instance, xml)
            instance.portal_type = self.typemapper(instance.portal_type)
            instance.reindexObject()
        finally:
            if removed:
                add_uid_namespace(self.marshaller)


class XMLContentRootExporter(object):
    implements(IFilesystemExporter)

    def __init__(self, context):
        self.context = context
        self.collector = collector.SimpleDictCollector()
        self.fse = XMLContentFSExporter(context, self.collector)
        self.manifest = manifest.ManifestWriter(StringIO())
        self.options = {}

    def set_options(self, **kwargs):
        self.options.update(kwargs)

    def get_options(self):
        return self.options

    def write_manifest(self, export_context, subdir):
        stream = StringIO()
        self.collector.getXml(stream)

        export_context.writeDataFile(MANIFEST,
                                     text         = stream.getvalue(),
                                     content_type = "text/xml",
                                     subdir       = subdir,
                                     )

        # XXX: refactor! this is only because we don't read from xml on import
        export_context.writeDataFile("MANIFEST.pickle", text=self.collector.getData(),
                content_type="application/octet-stream", subdir=subdir)

    def write_dot_objects(self, export_context, subdir):
        self.manifest.add(self.context.getId(), self.context.getPortalTypeName())
        export_context.writeDataFile('.objects.xml',
                                     text=self.manifest.getvalue(),
                                     content_type='text/xml',
                                     subdir=subdir,
                                     )

    def export(self, export_context, subdir, root=False):
        debug("XMLContentRootExporter.export: export_context=%s, subdir=%s, root=%s" % (
                export_context, subdir, root))

        # top-level .objects.xml
        self.write_dot_objects(export_context, subdir)

        # start export
        self.fse.set_options(**self.options)
        self.fse.export(export_context, subdir, root=False)

        # write export manifest
        self.write_manifest(export_context, subdir)

    def listExportableItems(self):
        return ()


class XMLContentFSExporter(object):
    implements(IFilesystemExporter)

    def __init__(self, context, collector=None):
        debug("XMLContentFSExporter.__init__: context=%s" % (context))
        self.context = context
        self.collector = collector
        self.ref_catalog = getToolByName(self.context, 'reference_catalog')

        # True if folder
        self.folderish = IBaseFolder.providedBy(context)
        debug("XMLContentFSExporter: context folderish: %s" % self.folderish)

        self.manifest = manifest.ManifestWriter(StringIO())
        self.options={}
        self.options["atns_exclude"] = []
        if config.NO_UID_ON_EXPORT:
            debug("GSXML: NO_UID_ON_EXPORT is True: UIDs will NOT be exported.")
            self.options["ignore_uid"] = True

    def set_options(self, **kwargs):
        self.options.update(kwargs)

    def get_options(self):
        return self.options

    # IFilesystemExporter
    def export(self, export_context, subdir, root=False):
        debug("XMLContentFSExporter.export: export_context=%s, subdir=%s, root=%s" % (
                export_context, subdir, root))

        # fetch an marshaller for this context
        serializer = IXMLMarshaller(self.context)

        if self.collector is not None:
            self.collector.addObjectInfo(self.context.UID(),
                                         subdir = subdir,
                                         UID    = self.context.UID(),
                                         id     = self.context.getId(),
                                         type   = self.context.portal_type,
                                        )

        # marshall binary data and record the field names for which we did so
        atns_exclude = self.exportFiles(export_context, subdir)


        # tell the marshaller to ignore the fields we exported the binary data
        self.options["atns_exclude"].extend(atns_exclude)

        # set marshaller options
        serializer.options = self.options

        # marshall references
        ref_info = self.exportReferences(export_context, subdir)
        if self.collector is not None:
            self.collector.addRefInfo(self.context.UID(), ref_info)

        # marshall our context
        fname = "%s.xml" % self.context.id
        path = os.path.join(subdir, fname)
        export_context.writeDataFile(path, serializer.xml, "text/xml")

        if not self.folderish:
            return

        if not root:
            subdir = '%s/%s' % (subdir, self.context.getId())
            debug("XMLContentFSExporter: root! subdir=%s" % subdir)

        # Because we are a folder, export all our contents, too.
        # for this we need to fetch a list of objects which are
        # containd in the context, and export those for which
        # we can get and adapter to IFilesystemExporter
        exportable = self.listExportableItems()

        for id, object, fse in exportable:
            if fse is None:
                continue
            # XXX: yuck!
            fse.collector = self.collector
            fse.export(export_context, subdir, False)
            self.manifest.add(id, object.getPortalTypeName())

        self.write_dot_objects(export_context, exportable, subdir)

    def exportReferences(self, export_context, subdir):
        """ Export the references stored in our context.
        """
        mime ="application/octet-stream"

        # pickle the references
        data = pickle.dumps(self.context.at_references.aq_base)

        # contrieve a sensible filename for the reference pickle
        filename = "%s.refs.pickle" % self.context.getId()

        # write the stuff out to the storage backend
        export_context.writeDataFile(filename,
                                     data,
                                     mime,
                                     subdir
                                    )
        if self.collector is not None:
                self.collector.addFileInfo( self.context.UID(), filename, mime )

        # now get some information about the references and
        # return them
        out = {}
        for ref in self.context.at_references.objectValues():
            ruid, info = self._getRefobjectInfo( ref )
            out[ruid] = info
        return out

    def _getRefobjectInfo(self, ref):
        """ Return a dict of information about one reference object.
        """
        return ref.UID(), dict(UID          = ref.UID(),
                               targetUID    = ref.targetUID,
                               sourceUID    = ref.sourceUID,
                               relationship = ref.relationship,
                               )


    def write_dot_objects(self, export_context, exportable, subdir):
        # export xml manifestns_exclude.append(field.getName())
        export_context.writeDataFile('.objects.xml',
                                     text = self.manifest.getvalue(),
                                     content_type = 'text/xml',
                                     subdir = subdir
                                     )

    def exportFiles( self, export_context, subdir):
        """ export any file based fields that aren't of type text/plain
            and return a list of field names exported in this fashion.
        """
        atns_exclude = []

        for field in self.context.Schema().fields():
            do_export = False
            if check_for_filefield(field):
                mime = field.getContentType(self.context)

                atns_exclude.append(field.getName())

                value = field.getRaw(self.context)
                if isinstance(value, File):
                    value = str(value.data)

                filename = utils.filename_for_field(field, self.context)

                export_context.writeDataFile(
                        filename,
                        value,
                        mime,
                        subdir
                    )

                if self.collector is not None:
                    self.collector.addFileInfo( self.context.UID(), filename, mime )

        return atns_exclude

    def listExportableItems(self):
        """
        Return a list of tuples of exportable items:
          (id, object, IFilesystemExporter(obj))

        i.e.
          [("anobjectid", <ATDocument object ...>, <ATDocumentFilesystemExporter object ...>), ("nonexportable", <object>, None), ...]
        """
        debug("listExportableItems: context.id=%s" % (self.context.id))
        if self.folderish:
            exportable = self.context.objectItems()
            exportable = [x + (IFilesystemExporter(x[1], None),) for x in exportable]
            debug("listExportableItems: exportable=%(exportable)s" % locals())
            return exportable
        else:
            return ()


class XMLContentRootImporter(object):
    """
    A controller for the import process.

    - reads and parses the Manifest
    - imports stuff
    - fix up imported objects
    """
    implements( IFilesystemImporter )

    def __init__(self, context ):
        # TODO: ensure context is folderish.
        self.context = context
        self.typemapper = component.queryUtility(ITypeMapper, default=lambda x: x)
        self.options={}

    def set_options(self, **kwargs):
        self.options.update(kwargs)

    def get_options(self):
        return self.options

    def _create_collector( self, import_context, subdir ):
        self.manifest = import_context.readDataFile( MANIFEST, subdir )
        if self.manifest is None:
            return

        # XXX: doit

        # XXX: too lazy to parse xml for now.
        data = import_context.readDataFile( "MANIFEST.pickle", subdir )
        if data is None:
            return

        self.collector = collector.SimpleDictCollector()
        self.collector.restoreData( data )

    def _fixup_import( self, import_context ):
        """
        Fixup the import.

        Here we ought to check whether or not reference UIDs changed during
        import. If so, we need to fix them. The sourceUID of the references
        is already fixed, the import step did that. So, we only need to
        check if reference target UIDs still match.

        We need to check every reference in the collector's reference map (which
        got built by the collector on import time) and check if a targetUID of those
        references has changed.
        """

        if self.collector is None:
            return # no fixup w/o collector info

        refmap = self.collector.getRefMap()

        ref_source_uids = refmap.keys()

        for sid, rm in refmap.iteritems():
            # XXX: this is lame. We need an adapter which adapts the changed reference to
            #      an conflict solver of some sort.
            if rm["new"] != rm["old"]:
                debug( "GSXML IMPORT: reference %(ref)s (%(url)s): sourceUID %(old)s -> %(new)s" % rm )

                target = rm["target"]

                if target in ref_source_uids:
                    old = refmap[target]["old"]
                    new = refmap[target]["new"]
                    debug( "GSXML IMPORT: FIXUP REFS: reference %(ref)s %(target)s -> %(new)s" % dict( ref=rm["ref"], new=new, target=target ) )

    def objects( self, import_context, subdir ):
        return manifest.ManifestReader( import_context.readDataFile('.objects.xml', subdir ) )

    def import_object(self, import_context, subdir, object_id, type_name, root=False):
        """ Import an object. Data is read from import_context using "subdir" and "object_id".
        """
        existing = self.context.objectIds()
        debug("XMLContentRootImporter.import_object: existing=%r" % (list(existing)))
        debug("XMLContentRootImporter.import_object: object_id=%s, type_name=%s" % (object_id, type_name))

        if object_id not in existing:
            id = _createObjectByType(type_name, self.context, object_id)
            if id is None:
                error( "XMLContentRootImporter: Could not create instance of type %s, id %s." % ( type_name, object_id ) )
                raise GSXMLImportError( "Could not create instance of type %s, id %s." % ( type_name, object_id ) )
            debug( "XMLContentRootImporter: Created object type %s, id %s." % ( type_name, object_id ) )

        object = self.context._getOb(object_id)
        if getattr(aq_base(object), 'unmarkCreationFlag', None) is not None:
            object.unmarkCreationFlag()

        fsi = IFilesystemImporter(object)
        fsi.set_options(**self.options)
        fsi.collector = self.collector
        fsi.import_(import_context, subdir, root=False)

    def import_(self, import_context, subdir, root=False):
        # create a collector object
        self._create_collector(import_context, subdir)

        for object_id, type_name in self.objects(import_context, subdir):
            # type mapping and skipping
            type_name = self.typemapper(type_name)
            if type_name == "skip":
                continue
            self.import_object(import_context, subdir, object_id, type_name, root=False)

        # fixup import
        self._fixup_import( import_context )


class XMLContentFSImporter(object):
    implements(IFilesystemImporter)

    def __init__( self, context, collector=None ):
        debug( "XMLContentFSImporter.__init__: context=%s" % ( context ) )
        # this is the object which was newly created or is to be updated
        self.context = context

        # now lets look up adapter which provides IXMLDemarshaller for
        # this object:
        self.demarshaller = IXMLDemarshaller( self.context )

        # store the collector
        self.collector = collector

        # reference catalog for ref munging
        self.ref_catalog = getToolByName(self.context, 'reference_catalog')

        self.folderish = IBaseFolder.providedBy( context )
        debug( "XMLContentFSImporter: context folderish: %s" % self.folderish )

        self.typemapper = component.queryUtility(ITypeMapper, default=lambda x: x)

        self.options = {}
        self.options["atns_exclude"] = []
        if config.NO_UID_ON_IMPORT:
            debug("GSXML: NO_UID_ON_IMPORT is True: UIDs will NOT be imported.")
            self.options["ignore_uid"] = True

    def set_options(self, **kwargs):
        self.options.update(kwargs)

    def get_options(self):
        return self.options

    def objects( self, import_context, subdir ):
        return manifest.ManifestReader( import_context.readDataFile('.objects.xml', subdir ) )

    # IFilesystemImporter
    def import_( self, import_context, subdir, root=False ):
        debug( "XMLContentFSImporter.import: import_context=%s, "
                "subdir=%s, root=%s" % ( import_context, subdir, root ) )

        id = self.context.getId()
        filename = "%s.xml" % id
        xml = import_context.readDataFile( filename, subdir )
        if xml is None:
            return

        # set options and demarshal
        self.demarshaller.options = self.options
        self.demarshaller.demarshall( self.context, xml )

        # XXX: lame. use an adapter.
        self.importFiles(import_context, subdir)

        # XXX: lame. use an adapter.
        self.importReferences(import_context, subdir)

        if not root:
            subdir = '%s/%s' % (subdir, self.context.getId())
        else:
            debug( "XMLContentFSImporter: root! subdir=%s" % subdir )

        if not self.folderish:
            return

        existing = self.context.objectIds()

        for object_id, type_name in self.objects(import_context, subdir):
            debug("XMLContentFSImporter.import: object_id=%s, type_name=%s" % (object_id, type_name))

            # type mapping and skipping
            type_name = self.typemapper(type_name)
            if type_name == "skip":
                continue

            if object_id not in existing:
                id = _createObjectByType(type_name, self.context, object_id)
                if id is None:
                    error( "XMLContentFSImporter: Could not create instance of type %s, id %s." % (type_name, object_id))
                    continue
                debug("XMLContentFSImporter: Created object type %s, id %s." % (type_name, object_id))

            object = self.context._getOb(object_id)
            if getattr(aq_base(object), 'unmarkCreationFlag', None) is not None:
                object.unmarkCreationFlag()

            fsi = IFilesystemImporter(object)
            fsi.set_options(**self.options)

            # XXX: lame. use Annotations to add the collector. Use an adapter.
            fsi.collector = self.collector
            fsi.import_(import_context, subdir)

    def importFiles( self, import_context, subdir ):
        for field in self.context.Schema().fields():
            filename = utils.filename_for_field(field, self.context)
            mimetype = None
            if self.collector:
                mimetype = self.collector.getMimeTypeForField(field, self.context)

            if check_for_filefield(field):
                value = import_context.readDataFile(filename, subdir)
                field.set(self.context, value)
                if mimetype:
                    field.setContentType(self.context, mimetype)



    def importReferences(self, import_context, subdir):
        if self.collector is not None:
            refmap = self.collector.getRefMap()
        else:
            refmap = {}

        # read the binary pickle file
        refs = import_context.readDataFile("%s.refs.pickle" % self.context.getId(), subdir)
        if refs is None:
            return

        try:
            references = pickle.loads(refs)
        # XXX: ImportError
        except:
            return {}


        # ... boom! restore references and
        self.context.at_references = pickle.loads(refs)

        # ... fix them up. We make sure that at least the source
        # UID is correct at this time.
        for ref in self.context.at_references.objectValues():
            url = getRelURL(self.context.at_references, ref.getPhysicalPath())

            # record this change
            refmap[ref.sourceUID] = {"new": self.context.UID(), "old": ref.sourceUID, "target": ref.targetUID, "ref": ref.UID, "url": url }

            # update the reference source
            ref.sourceUID = self.context.UID()
            self.ref_catalog.catalog_object( ref, url )

        return refmap


# vim: set ft=python ts=4 sw=4 expandtab :
