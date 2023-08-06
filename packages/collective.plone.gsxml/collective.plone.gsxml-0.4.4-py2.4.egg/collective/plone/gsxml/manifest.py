#  -*- coding: utf-8 -*-
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
#
"""Manifest writer
"""

__author__ = """Kapil Thangavelu <k_vertigo@objectrealms.net>"""
__docformat__ = 'restructuredtext'
__revision__ = "$Revision: 41534 $"

from xml.sax import parseString, ContentHandler

class ManifestReader( object ):

    def __init__(self, manifest_body ):
        self.data = []
        if manifest_body is None:
            return

        handler = ManifestParser()
        parseString( manifest_body, handler )
        self.data = handler.getData()

    def __iter__(self):
        return iter( self.data )


class ManifestParser( ContentHandler ):

    def __init__(self):
        self._data = []
        self._last = ""
        self._chars = []

    def getData( self ):
        return self._data

    def startElement( self, name, attrs ):
        if name == u'record':
            self._last = attrs.get('type','')

    def endElement( self, name ):
        if name == 'record':
            self._data.append( ("".join(self._chars).strip(), self._last) )
        self._chars = []

    def characters( self, buffer ):
        self._chars.append( buffer )


class ManifestWriter( object ):

    def __init__( self, stream ):
        self.stream = stream
        self.closed = False
        print >> stream, "<manifest>"

    def add( self, object_id, object_type ):
        print >> self.stream, '<record type="%s">'%object_type, object_id, '</record>'

    def getvalue(self):
        if not self.closed:
            print >> self.stream, "</manifest>"
        self.closed = True
        return self.stream.getvalue()


# vim: set filetype=python ts=4 sw=4 expandtab :
