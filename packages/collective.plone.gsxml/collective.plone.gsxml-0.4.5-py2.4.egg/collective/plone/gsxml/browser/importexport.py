# -*- coding: utf-8 -*-
#
# File: .py
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

__author__    = """Stefan Eletzhofer <stefan.eletzhofer@inquant.de>"""
__docformat__ = 'plaintext'
__revision__  = "$Revision: 67182 $"
__version__   = '$Revision: 67182 $'[11:-2]


import logging
import xmlrpclib
from StringIO import StringIO

from zope import interface
from zope import component

from Products.Five.browser import BrowserView

from collective.plone.gsxml.interfaces import IImportExportView

from collective.plone.gsxml.content import XMLContentRootImporter
from collective.plone.gsxml.content import XMLContentFSImporter
from collective.plone.gsxml.context import TarballImportContext

from collective.plone.gsxml.content import XMLContentRootExporter
from collective.plone.gsxml.content import XMLContentFSExporter
from collective.plone.gsxml.context import TarballExportContext


info = logging.getLogger("gsxml.importexport").info


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
        def meta_dict(name, obj):
            return dict(
                    name=name,
                    UID=obj.UID(),
                    portal_type=obj.portal_type,
                    modified=obj.modification_date,
                    url=obj.absolute_url(),
                    path="/".join(obj.getPhysicalPath())
                    )
        return [meta_dict(name, obj) for name, obj, _ in items]

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
