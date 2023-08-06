# -*- coding: utf-8 -*-
#
# File: config.py
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

PROJECTNAME = 'collective.plone.gsxml'
GLOBALS = globals()

# set this to true if you d NOT want to export the
# UIDs of your objects.
NO_UID_ON_EXPORT=True
NO_UID_ON_IMPORT=True

# Set this to false if you want FileFields containing
# text exported INLINE the xml.
# XXX: Setting this to false currently breaks because
#      OFS.File is not unicode aware. yuck.
EXPORT_TEXT_AS_FILE=True

# vim: set ft=python ts=4 sw=4 expandtab :

