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
__revision__  = "$Revision: 77619 $"
__version__   = '$Revision: 77619 $'[11:-2]


from zope.interface import implements
from zope.lifecycleevent import ObjectModifiedEvent

from interfaces import IObjectWillBeImportedEvent
from interfaces import IObjectImportedEvent
from interfaces import IObjectWillBeExportedEvent
from interfaces import IObjectExportedEvent


class ObjectWillBeExportedEvent(ObjectModifiedEvent):
    """Event fired just before a object gets exported"""
    implements(IObjectWillBeExportedEvent)

class ObjectExportedEvent(ObjectModifiedEvent):
    """Event fired after a object got exported"""
    implements(IObjectExportedEvent)

class ObjectWillBeImportedEvent(ObjectModifiedEvent):
    """Event fired just before an object is going to be imported.

    The object passed has been already created and is the instance that will be
    filled by the Marshaller.
    """
    implements(IObjectWillBeImportedEvent)

class ObjectImportedEvent(ObjectModifiedEvent):
    """Event fired after an object has been imported"""
    implements(IObjectImportedEvent)


# vim: set ft=python ts=4 sw=4 expandtab :
