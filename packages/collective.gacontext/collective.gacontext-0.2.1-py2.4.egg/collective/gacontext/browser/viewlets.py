# -*- coding: utf-8 -*-
#
# File: viewlets.py
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
__revision__  = "$Revision: 60983 $"
__version__   = '$Revision: 60983 $'[11:-2]

from zope import component
from plone.app.layout.viewlets.common import ViewletBase
from Products.CMFPlone.utils import safe_unicode
from collective.gacontext.interfaces import IGAFinder

class GAViewlet(ViewletBase):

    def __init__(self, context, request, view, manager):
        super(GAViewlet, self).__init__(context, request, view, manager)
        self.context = context
        self.gafinder = component.queryUtility(IGAFinder)

    def update(self):
        pass

    def render(self):
        """render the webstats snippet"""
        if self.gafinder and self.gafinder(self.context):
            return safe_unicode(self.gafinder(self.context))
        else:
            return ''

# vim: set ft=python ts=4 sw=4 expandtab :
