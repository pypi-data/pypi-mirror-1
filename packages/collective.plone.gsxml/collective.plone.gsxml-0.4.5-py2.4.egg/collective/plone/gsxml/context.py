# -*- coding: utf-8 -*-
#
# File: context.py
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
__revision__  = "$Revision: 59938 $"
__version__   = '$Revision: 59938 $'[11:-2]

import os
import logging
import time
from StringIO import StringIO
from tarfile import TarFile
from tarfile import TarInfo

from DateTime.DateTime import DateTime
from zope.interface import implements
from Products.GenericSetup.interfaces import IExportContext, IImportContext
from interfaces import IFSEnv


SKIPPED_FILES = ('CVS', '.svn', '_svn', '_darcs')
SKIPPED_SUFFIXES = ('~',)

LOGGER="gsxml.context"

def info(msg):
    logging.getLogger(LOGGER).info(msg)

def debug(msg):
    logging.getLogger(LOGGER).debug(msg)

def error(msg):
    logging.getLogger(LOGGER).error(msg)

class DummyContext(object):
    implements(IExportContext, IImportContext)

    def __init__(self):
        self.brain={}

    def writeDataFile(self, filename, text, content_type, subdir=None):
        if subdir is not None:
            fn = os.path.join( subdir, filename )
        else:
            fn = filename

        self.brain[fn] = text

    def readDataFile( self, filename, subdir=None ):
        if subdir is not None:
            fn = os.path.join( subdir, filename )
        else:
            fn = filename

        return self.brain[fn]


class TarballImportContext(object):
    """ Import Data to Tarball
    """
    implements(IImportContext)

    def __init__( self, fileobj, mode="r:gz" ):
        """ init Tarball import
        """
        self._archive = TarFile.open( 'foo.bar', mode, fileobj )


    def readDataFile( self, filename, subdir=None ):
        """ See IImportContext.
        """
        info( "TarballImportContext.readDataFile: filename=%s, subdir=%s" % (filename, subdir) )
        if subdir is not None:
            filename = '/'.join( ( subdir, filename ) )
            info( "TarballImportContext.is_subdir: filename=%s" % (filename) )

        try:
            file = self._archive.extractfile( filename )
            info("TarballImportContext: extracted filename=%s" % (filename) )
        except KeyError:
            info("TarballImportContext: could not extract filename=%s" % (filename) )
            return None

        return file.read()

    def getLastModified( self, path ):

        """ See IImportContext.
        """
        info = self._getTarInfo( path )
        return info and info.mtime or None

    def isDirectory( self, path ):

        """ See IImportContext.
        """
        info = self._getTarInfo( path )

        if info is not None:
            return info.isdir()

    def listDirectory(self, path, skip=SKIPPED_FILES,
                      skip_suffixes=SKIPPED_SUFFIXES):

        """ See IImportContext.
        """
        if path is None:  # root is special case:  no leading '/'
            path = ''
        else:
            if not self.isDirectory(path):
                return None

            if path[-1] != '/':
                path = path + '/'

        pfx_len = len(path)

        names = []
        for name in self._archive.getnames():
            if name == path or not name.startswith(path):
                continue
            name = name[pfx_len:]
            if '/' in name or name in skip:
                continue
            if [s for s in skip_suffixes if name.endswith(s)]:
                continue
            names.append(name)

        return names

    def shouldPurge( self ):

        """ See IImportContext.
        """
        return self._should_purge

    def _getTarInfo( self, path ):
        if path[-1] == '/':
            path = path[:-1]
        try:
            return self._archive.getmember( path )
        except KeyError:
            pass
        try:
            return self._archive.getmember( path + '/' )
        except KeyError:
            return None


class TarballExportContext(object):
    """
    Eport Data to Tarball
    """
    implements(IExportContext)

    def __init__(self, fileobj=None, archive_name=None, mode="w:gz"):
        """
        inits the tar file
        """
        info( "TarballExportContext:__init__() fileobj=%s, archive_name=%s, mode=%s" % (fileobj, archive_name, mode) )

        if archive_name is None:
            timestamp = time.gmtime()
            archive_name = ( 'gsxml-%4d%02d%02d%02d%02d%02d.tar.gz'
                           % timestamp[:6] )
            info( "setting filename to %s" % archive_name )

        if fileobj is None:
            fileobj = StringIO()

        self.fileobj = fileobj
        self._archive_filename = archive_name
        self._archive = TarFile.open( archive_name, mode, fileobj )


    def writeDataFile(self, filename, text, content_type, subdir=None):
        """
        See IExportContext
        """
        if subdir is not None:
            filename = '/'.join( ( subdir, filename ) )

        stream = StringIO( text )
        info = TarInfo( filename )
        info.size = len( text )
        info.mtime = time.time()
        self._archive.addfile( info, stream )

    def getArchive( self ):
        """ Close the archive, and return it as a big string.
        """
        self._archive.close()
        return self.fileobj.getvalue()

    def getArchiveStream( self ):
            """
            Returns a filelike object
            """
            self._archive.close()
            return self.fileobj

    def getArchiveFilename( self ):
        """
        Return the Filename of the Archive
        """
        return self._archive_filename

    def getArchiveSize(self):
        """
        Returns the length of the tar data
        """
        return len( self.fileobj.getvalue() )


class SimpleFSExportContext(object):
    implements(IExportContext)

    def __init__(self, root):
        #self.dirname = os.path.join( os.environ["HOME"], root )
        self.dirname = root

        if not os.path.isdir(self.dirname):
            debug("simpleFSExportContext.__init__: make dirs: %s" % self.dirname)
            os.makedirs(self.dirname)

    def writeDataFile(self, filename, text, content_type, subdir=None):
        debug("simpleFSExportContext.writeDataFile: filename=%s, subdir=%s, content_type=%s" % (
                filename, subdir, content_type))

        dir, filename = os.path.split(filename)

        # concatenate the full path to the file
        if subdir is not None:
            dir = os.path.join(self.dirname, subdir, dir)
        else:
            dir = os.path.join(self.dirname, dir)

        fullpath = os.path.join(dir, filename)

        if not os.path.isdir(dir):
            os.makedirs(dir)
            debug("simpleFSExportContext.writeDataFile: make dirs: %s" % dir)

        info("simpleFSExportContext.writeDataFile: fullpath=%s" % fullpath)
        file(fullpath, "wb").write(text)


class SimpleFSImportContext(object):
    implements( IImportContext )

    # XXX: hack: the GS code references this but its NOT in the IImportContext
    #            Interface. Doh.
    def getLogger(self, *args, **kw):
        return logging.getLogger(*args, **kw)

    def __init__(self, root):
        debug("SimpleFSImportContext.__init__: root=%s" % (root))
        #self.dirname = os.path.join(os.environ["HOME"], root)
        self.dirname = root

    def readDataFile(self, filename, subdir=None):
        debug("SimpleFSImportContext.readDataFile: filename=%s, subdir=%s" % (filename, subdir))

        if subdir is None:
            full_path = os.path.join(self.dirname, filename)
        else:
            full_path = os.path.join(self.dirname, subdir, filename)

        if not os.path.exists(full_path):
            return None

        file = open(full_path, 'rb')
        result = file.read()
        file.close()
        return result

    def getLastModified( self, path ):
        debug("SimpleFSImportContext.getLastModified: path=%s" % (path))
        full_path = os.path.join( self.dirname, path )

        if not os.path.exists(full_path):
            return None
        return DateTime(os.path.getmtime(full_path))

    def isDirectory(self, path):
        debug("SimpleFSImportContext.isDirectory: path=%s" % (path))
        full_path = os.path.join(self.dirname, path)

        if not os.path.exists(full_path):
            return None

        return os.path.isdir(full_path)

    def listDirectory(self, path, skip=SKIPPED_FILES, skip_suffixes=SKIPPED_SUFFIXES):
        debug("SimpleFSImportContext.listDirectory: path=%s" % (path))
        if path is None:
            path = ''

        full_path = os.path.join(self.dirname, path)

        if not os.path.exists(full_path) or not os.path.isdir(full_path):
            return None

        names = []
        for name in os.listdir(full_path):
            if name in skip:
                continue
            if [s for s in skip_suffixes if name.endswith(s)]:
                continue
            names.append(name)

        return names


class DictFSEnv(object):
    """ stores data into a dictionary with a fs like manner
    """
    implements(IFSEnv)

    def __init__(self, brain={}):
        """ initialize the storage with a dictionary
        """
        debug("DictFSEnv: __init__: %(brain)s" % locals())
        self.brain = brain

    def lookup(self, path):
        dirs = path.split(os.sep)
        current = self.brain
        for dir in dirs:
            current = current[dir]
        return current

    def write(self, path, content):
        debug("DictFSEnv: write: %(path)s" % locals())
        dirs, filename = os.path.split(path)
        dirs = dirs.split(os.sep)

        current = self.brain

        for dir in dirs:
            if not current.has_key(dir):
                current[dir] = {}
            current = current[dir]

        current[filename] = content

    def read(self, path):
        debug("DictFSEnv: read: %(path)s" % locals())
        dirs, filename = os.path.split(path)
        dirs = dirs.split(os.sep)

        current = self.brain
        for dir in dirs:
            debug("DictFSEnv: read: traverse to %(dir)s" % locals())
            if current.has_key(dir):
                current = current[dir]
            else:
                return None

        return current[filename]

    def listdir(self, path):
        """
        Returns the "files" stored in path

        >>> fs = DictFSEnv({})
        >>> fs.write( "huhu/zonk/blah/a", "a" )
        >>> fs.write( "huhu/zonk/blah/b", "b" )
        >>> fs.write( "huhu/zonk/blah/c", "c" )
        >>> listdir( "huhu/zonk/blah" )
        [ "a", "b", "c" ]
        """
        debug("DictFSEnv: listdir: %(path)s" % locals())
        return self.lookup(path).keys()

    def isdir(self, path):
        info("DictFSEnv: isdir: %(path)s" % locals())
        d = self.lookup(path)
        if type(d) == type({}):
            return True
        else:
            return False

    def exists(self, path):
        debug("DictFSEnv: exists: %(path)s" % locals())
        try:
            d = self.lookup(path)
            return True
        except KeyError:
            return False

# vim: set ft=python ts=4 sw=4 expandtab :
