# -*- coding: utf-8 -*-
#
# File: collector.py
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
__revision__ = "$Revision: 60124 $"

import logging
import pickle
import datetime

import utils

LOGGER="gsxml.collector"
def info(msg):
    logging.getLogger(LOGGER).info(msg)

def debug(msg):
    logging.getLogger(LOGGER).debug(msg)

def error(msg):
    logging.getLogger(LOGGER).error(msg)

class SimpleDictCollector(object):
    # implements( IExportDataCollector )

    def __init__(self, brain={} ):
        self.brain = brain
        self.starttime = ""
        self.endtime = ""
        self.refmap = {}

    def _setInfo( self, uid, key, i ):
        d = self.brain.get( uid, {} )
        self.brain[uid] = d

        dd = d.get( key, {} )
        d[key] = dd

        dd.update(i)

    def _getInfo( self, uid, key ):
        d = self.brain.get( uid, {} )
        self.brain[uid] = d
        
        dd = d.get( key, {} )
        d[key] = dd

        return dd

    def getRefMap(self):
        return self.refmap

    def getRefXml( self, ref, stream ):
        print >>stream, "<reference uid='%(UID)s' sourceUID='%(sourceUID)s' targetUID='%(targetUID)s' relationship='%(relationship)s'/>" % ref

    def getReferencesXml( self, uid, stream ):
        references = self._getInfo( uid, "references" )
        print >>stream, "<references>"
        for ref in references.values():
            self.getRefXml( ref, stream )
        print >>stream, "</references>"

    def getFilesXml( self, uid, stream ):
        fileinfo = self._getInfo( uid, "files" )
        print >>stream, "<files>"
        for f in fileinfo.values():
            print >>stream, "<file filename='%(filename)s' mimetype='%(mimetype)s'/>" % f
        print >>stream, "</files>"

    def getObjectsXml( self, stream ):
        for uid, info in self.brain.iteritems():
            print >>stream, "<object uid='%(UID)s' name='%(id)s' subdir='%(subdir)s'>" % info
            self.getReferencesXml( uid, stream )
            self.getFilesXml( uid, stream )
            print >>stream, "</object>"

    def getXml( self, stream ):
        print >>stream, "<exportinfo starttime='%s' endtime='%s'>" % ( self.starttime, self.endtime )
        self.getObjectsXml( stream )
        print >>stream, "</exportinfo>"

    def getData( self ):
        return pickle.dumps( self.brain )

    def restoreData( self, bin ):
        self.brain = pickle.loads( bin )

    def addRefInfo( self, uid, info ):
        self._setInfo( uid, 'references', info )

    def addFileInfo( self, uid, filename, mimetype ):
        files = self._getInfo( uid, "files" )
        files[filename] = dict( filename=filename, mimetype=mimetype )
        self._setInfo( uid, "files", files )

    def addObjectInfo( self, uid, **kwargs ):
        d = self.brain.get( uid, {} )
        self.brain[uid] = d

        d.update( kwargs ) 

    def getUIDs( self ):
        return self.brain.keys()

    def getFiles( self, uid ):
        return self._getInfo( uid, "files" )

    def getMimeTypeForField(self, field, context):
        filename = utils.filename_for_field(field, context)
        inf = self.brain.get(context.UID())
        if not inf:
            return None
        file_info = inf.get("files")
        if not file_info:
            return None

        fi = file_info.get(filename)
        if not fi:
            return None

        return fi["mimetype"]

    def setStart( self ):
        self.starttime = datetime.datetime.now().isoformat()

    def setEnd( self ):
        self.endtime = datetime.datetime.now().isoformat()

# vim: set ft=python ts=4 sw=4 expandtab :
