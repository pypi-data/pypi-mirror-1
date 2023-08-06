# -*- coding: utf-8 -*-
#
# File: rootmanifest.py
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

__author__ = """Stefan Eletzhofer <stefan.eletzhofer@inquant.de>"""
__docformat__ = 'plaintext'
__revision__ = "$Revision: 41635 $"

import elementtree.ElementTree as ET

def make_refinfo( element ):
    return RefInfo( **dict( element.items() ) )

def make_fileinfo( element ):
    return FileInfo( **dict( element.items() ) )

def make_objectinfo( element ):
    d = dict( element.items() )
    r = []
    f = []

    for ref in element.getiterator( tag="reference" ):
        r.append( make_refinfo( ref ) )

    for fl in element.getiterator( tag="file" ):
        f.append( make_fileinfo( fl ) )

    return ObjectInfo( references=r, files=f, **d )

class NodeInfo( object ):
    _attrs = []
    def __init__( self, **kwargs ):
        self.__dict__.update( dict.fromkeys( self._attrs ) )
        self.__dict__.update( kwargs )
    def __repr__(self):
        return "<%s %s >" % ( self.__class__.__name__, " ".join(["%s=%s" % (k, self.__dict__[k]) for k in self._attrs] ) )

class FileInfo( NodeInfo ):
    _attrs = [ "mimetype", "filename" ]

class RefInfo( NodeInfo ):
    _attrs = [ "uid", "sourceUID", "targetUID", "relationship" ]

class ObjectInfo( NodeInfo ):
    _attrs = [ "uid", "name", "subdir" ]


class RootManifestReader( object ):
    def __init__( self, manifest ):
        self.tree = ET.parse( manifest )
        self._objects = {}

        self.parse( self.tree )

    def parse( self, tree ):
        for o in tree.getiterator( tag="object" ):
            oi = make_objectinfo( o )
            self._objects[oi.uid] = oi

    def getObjectUIDs( self ):
        return self._objects.keys()

    def getObjectByUID( self, uid ):
        return self._objects[uid]


if __name__ == "__main__":
    rmr = RootManifestReader( "MANIFEST.XML" )

    for uid in rmr.getObjectUIDs():
        o =rmr.getObjectByUID( uid )
        print "UID:", uid, o
        print "        files:", ",".join([ "'%s'" % f.filename for f in o.files ])
        print "        refs:", o.references


# vim: set ft=python ts=4 sw=4 expandtab :
