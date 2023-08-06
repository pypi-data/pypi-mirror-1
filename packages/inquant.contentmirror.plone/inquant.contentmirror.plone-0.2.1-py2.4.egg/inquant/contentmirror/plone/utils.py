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

__author__    = """Stefan Eletzhofer <stefan.eletzhofer@inquant.de>"""
__docformat__ = 'plaintext'
__revision__  = "$Revision: 57036 $"
__version__   = '$Revision: 57036 $'[11:-2]

# portions of this code is copied from OFS.CopySupport

import logging

from marshal import loads
from urllib import unquote
from zlib import decompress

from Acquisition import aq_base
from ZODB.POSException import ConflictError
from OFS import Moniker

from zope.app.component.hooks import getSite

info = logging.getLogger().info

def _cb_decode(s):
    return loads(decompress(unquote(s)))

def get_copy_objects( cb_copy_data=None, REQUEST=None ):
    """ return a list of objects from the clipboard """

    cp = None
    if cb_copy_data is not None:
        cp = cb_copy_data
    elif REQUEST is not None and REQUEST.has_key('__cp'):
        cp = REQUEST['__cp']

    if cp is None:
        raise AttributeError( "no copy data" )

    try:
        op, mdatas = _cb_decode(cp)
    except:
        raise AttributeError( "invalid copy data" )

    oblist = []
    app = getSite().getPhysicalRoot()
    for mdata in mdatas:
        m = Moniker.loadMoniker(mdata)
        try:
            ob = m.bind(app)
        except ConflictError:
            raise
        except:
            raise AttributeError( "object not found" )
        oblist.append(ob)

    return oblist

def give_new_context(obj, context):
    obj = aq_base(obj)
    obj = obj.__of__(context)
    return obj


# vim: set ft=python ts=4 sw=4 expandtab :
