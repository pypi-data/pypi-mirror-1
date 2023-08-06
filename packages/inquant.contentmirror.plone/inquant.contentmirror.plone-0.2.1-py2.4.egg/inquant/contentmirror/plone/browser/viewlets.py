
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
from zope.interface import implements
from zope.viewlet.interfaces import IViewlet

from Acquisition import aq_inner, aq_parent
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from Products.statusmessages.interfaces import IStatusMessage

from inquant.contentmirror.base.interfaces import IMirroredContent
from inquant.contentmirror.base.interfaces import IMirroredContentManager
from inquant.contentmirror.base.interfaces import IMirrorReferenceManager


class MirrorInfoViewlet(BrowserView):
    """ Viewlet to show some info if the ccurrent context is a mirror. Also allows to remove the mirror.
    """
    implements(IViewlet)
    render = ViewPageTemplateFile('mirror-info.pt')

    def __init__(self, context, request, view, manager):
        super(MirrorInfoViewlet, self).__init__(context, request)
        self.__parent__ = view
        self.view = view
        self.container = aq_parent(aq_inner(self.context))
        self.manager = component.getUtility(IMirroredContentManager)
        self.refmgr = IMirrorReferenceManager(self.context)

    def update(self):
        if not self.available():
            return

        if self.request.has_key('inquant.contentmirror.plone.remove'):
            self.manager.removeMirror(self.context, self.container)
            IStatusMessage(self.request).addStatusMessage("Removed mirror.", type="info")
            self.request.response.redirect(self.container.absolute_url())

    def available(self):
        if not IMirroredContent.providedBy(self.context):
            return False
        return self.refmgr.isMirror(self.context, self.container)

    def original_url(self):
        return self.refmgr.getOriginal().absolute_url()


# vim: set ft=python ts=4 sw=4 expandtab :
