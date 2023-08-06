# -*- coding: utf-8 -*-
#
# File: interfaces.py
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
__revision__  = "$Revision: 67174 $"
__version__   = '$Revision: 67174 $'[11:-2]

from zope import schema
from zope.interface import Interface, Attribute

class IFilesystemExporter(Interface):
    """ Plugin interface for site structure export.
    """
    def export(export_context, subdir, root=False):
        """ Export our 'context' using the API of 'export_context'.

        o 'export_context' must implement
          Products.GenericSupport.interfaces.IExportContext.

        o 'subdir', if passed, is the relative subdirectory containing our
          context within the site.

        o 'root', if true, indicates that the current context is the
          "root" of an import (this may be used to adjust paths when
          interacting with the context).
        """

    def listExportableItems():
        """ Return a sequence of the child items to be exported.

        o Each item in the returned sequence will be a tuple,
          (id, object, adapter) where adapter must implement
          IFilesystemExporter.
        """

    def set_options(**kwargs):
        """ set additional options for marshallers """

    def get_options():
        """ return set options """

class IFilesystemImporter(Interface):
    """ Plugin interface for site structure export.
    """
    def import_(import_context, subdir, root=False):
        """ Import our 'context' using the API of 'import_context'.

        o 'import_context' must implement
          Products.GenericSupport.interfaces.IImportContext.

        o 'subdir', if passed, is the relative subdirectory containing our
          context within the site.

        o 'root', if true, indicates that the current context is the
          "root" of an import (this may be used to adjust paths when
          interacting with the context).
        """

    def set_options(**kwargs):
        """ set additional options for marshallers """

    def get_options():
        """ return set options """


class IXMLExportableContent(Interface):
    """
    A marker interface for all content which is exportable as
    XML in some ways. Objects marked in that way must implement IFilesystemExporter
    and IFilesystemImporter (or have adapters).
    """

class IXMLMarshaller(Interface):
    """
    An Interface that delivers xml
    """
    xml = Attribute(u"the XML representation of the content")

class IXMLDemarshaller(Interface):
    """
    An interface for objects which can demarshall xml to an
    existing object instance.
    """
    def demarshall( instance, xml ):
        """
        Demarshall the xml to the supplied object instance.
        """

class ITarConfig(Interface):
    """
    A Tar Import/Export Form
    """
    path = schema.Bytes(title=u'Path',
                           description=u'Select a Tar File',
                           required=True)


class ITypeMapper(Interface):
    def __call__(portal_type):
        """ returns a portal type to be used
        """

class IXMLMorpher(Interface):
    def __call__(xml):
        """ mangles/modifies/whatever the input xml and returns the changed xml
        """

class IExportXMLMorpher(IXMLMorpher):
    pass

class IImportXMLMorpher(IXMLMorpher):
    pass

class IImportExportView(Interface):
    """ foo """

    def gsxml_export(path):
        """ export path and return a tarball """

    def gsxml_import(data, path):
        """ import to path from tarball data """

    def list_exportable_items(self, path):
        """ list exportable items in path """


class IFSEnv(Interface):
    """ An interface for objects which want to store data in a fs like environment
    """
    def write(path, content):
        """ create a "file" with the content
        """

    def read(path):
        """ read the content of a file
        """

    def listdir(path):
        """ list the content of the directory
        """

    def isdir(path):
        """ checks for file/directory
        """

    def exists(path):
        """ checks if the path exists
        """

    def lookup(path):
        """
        """

# vim: set ft=python ts=4 sw=4 expandtab :
