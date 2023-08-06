# -*- coding: utf-8 -*-
#
# File: utils.py
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
__revision__  = "$Revision: 60124 $"
__version__   = '$Revision: 60124 $'[11:-2]

import mimetypes
from Products.Archetypes.utils import contentDispositionHeader


def download_file( RESPONSE, file, name, size, mime_type="text/UTF-8" ):
    """ direct file download
    """
    RESPONSE.setHeader('Content-Length', size )
    RESPONSE.setHeader('Content-Type', mime_type )
    header_value = contentDispositionHeader('attachment', "utf-8", filename=name )
    RESPONSE.setHeader("Content-disposition", header_value)
    file.seek(0)
    return file.read()

def filename_for_field(field, context):
    return "%s.%s.data" % (context.getId(), field.getName())

def guess_extension( mime_type ):

    extensions = mimetypes.guess_all_extensions( mime_type )

    # default lib returns uncommon default extensions for these,
    # short circuit then.

    if mime_type.startswith('text/plain') and '.txt' in extensions:
        return '.txt'

    elif mime_type.startswith('image/jpeg') and '.jpg' in extensions:
        return '.jpg'

    return mimetypes.guess_extension( mime_type )


# vim: set ts=4 sw=4 expandtab:
