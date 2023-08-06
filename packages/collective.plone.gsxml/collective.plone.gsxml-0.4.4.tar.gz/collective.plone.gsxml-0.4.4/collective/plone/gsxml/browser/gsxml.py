# -*- coding: utf-8 -*-
#
# File: gsxml.py
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
__revision__  = "$Revision: 67012 $"
__version__   = '$Revision: 67012 $'[11:-2]

import os
import logging
import xmlrpclib
from StringIO import StringIO

from zope import interface
from zope import component

from zope.formlib import form
from Products.Five.formlib import formbase

from Products.Five import BrowserView

# import gsxml stuff
from collective.plone.gsxml.interfaces import ITarConfig
from collective.plone.gsxml.context import TarballImportContext, TarballExportContext
from collective.plone.gsxml.context import SimpleFSImportContext, SimpleFSExportContext
from collective.plone.gsxml.content import XMLContentRootImporter
from collective.plone.gsxml.content import XMLContentRootExporter
from collective.plone.gsxml.content import XMLContentFSExporter

from collective.plone.gsxml import utils


info = logging.getLogger("gsxml").info


class FSExport(BrowserView):

    def __init__(self, context, request):
        super(FSExport, self).__init__(context, request)

    def __call__(self):
        """ export to a fixed location """
        dirname = os.path.join(os.environ["HOME"])

        ex = XMLContentRootExporter(self.context)
        ec = SimpleFSExportContext(dirname)

        ex.export(ec, "structure", False)



class FSImport(formbase.PageForm):

    def __init__(self, context, request):
        super(FSImport, self).__init__(context, request)

    def __call__(self):
        """ import from a fixed location """
        dirname = os.path.join(os.environ["HOME"])
        im = XMLContentRootImporter(self.context)
        ic = SimpleFSImportContext(dirname)
        im.import_(ic, "structure", False)



class Export(BrowserView):

    def __init__(self, context, request):
        super(Export, self).__init__(context, request)

    def __call__(self):
        ex = XMLContentRootExporter(self.context)
        ec = TarballExportContext()
        ex.export(ec, "structure", False)

        file = ec.getArchiveStream()
        name = ec.getArchiveFilename()
        size = ec.getArchiveSize()

        return utils.download_file( self.request.RESPONSE, file, name, size, mime_type="application/x-tar" )


class Import(formbase.PageForm):
    form_fields = form.FormFields(ITarConfig)
    label = "GSXML"

    @form.action("upload tar-file")
    def action_import(self, action, data):
        """ import from a given location """
        im = XMLContentRootImporter(self.context)
        ic = TarballImportContext(StringIO(data["path"]))
        im.import_(ic, "structure", False)

class IImportExportView(interface.Interface):
    """ foo """

    def gsxml_export(path):
        """ export path and return a tarball """

    def gsxml_import(data, path):
        """ import to path from tarball data """

    def list_exportable_items(self, path):
        """ list exportable items in path """

class ImportExportView(BrowserView):
    """ docs """
    interface.implements(IImportExportView)

    def __call__(self):
        return "Mooo!"

    def gsxml_export(self, path):
        """ export path and return a tarball """
        info("ImportExportView: gsxml_export(path=%s)" % path)
        context = self.context.restrictedTraverse(path)
        ex = XMLContentRootExporter(context)
        ec = TarballExportContext()
        ex.export(ec, "structure", False)

        file = ec.getArchiveStream()
        name = ec.getArchiveFilename()
        size = ec.getArchiveSize()
        return dict(
                data=xmlrpclib.Binary(file.getvalue()),
                name=name,
                size=size
                )

    def list_exportable_items(self, path):
        """ list GSXML exportable items """
        info("ImportExportView: list_exportable_items(path=%s)" % (path))
        context = self.context.restrictedTraverse(path)
        ex = XMLContentFSExporter(context)
        items = ex.listExportableItems()
        return [(name, obj.portal_type) for name, obj, _ in items]

    def gsxml_import(self, data, path):
        """ import to path from tarball data """
        info("ImportExportView: gsxml_import(data=%s, path=%s)" % (repr(data), path))
        if isinstance(data, xmlrpclib.Binary):
            data = data.data
        context = self.context.restrictedTraverse(path)
        im = XMLContentRootImporter(context)
        ic = TarballImportContext(StringIO(data))
        return im.import_(ic, "structure", False)

# vim: set ft=python ts=4 sw=4 expandtab :
