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
__revision__  = "$Revision: 62294 $"
__version__   = '$Revision: 62294 $'[11:-2]

from zope import component

from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from Products.statusmessages.interfaces import IStatusMessage

from inquant.contentmirror.base.interfaces import IMirroredContentManager
from inquant.contentmirror.plone.utils import get_copy_objects

class MirrorAddView(BrowserView):
    """
    """
    def __init__(self, context, request):
        super(MirrorAddView, self).__init__(context, request)
        self.copy_objects = get_copy_objects(REQUEST=request)
        self.manager = component.getUtility(IMirroredContentManager)

    def __call__(self):
        added = []
        for o in self.copy_objects:
            self.manager.addMirror(o, self.context)
            added.append(o.getId())

        IStatusMessage(self.request).addStatusMessage("Added mirror(s) of %s" % ",".join(added), type="info")
        self.request.response.redirect(self.context.absolute_url())

# vim: set ft=python ts=4 sw=4 expandtab :
