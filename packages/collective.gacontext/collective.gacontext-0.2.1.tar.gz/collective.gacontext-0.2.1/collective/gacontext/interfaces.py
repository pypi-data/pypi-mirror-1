# -*- coding: utf-8 -*-
#
# File: interfaces.py
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
__revision__  = "$Revision: 60982 $"
__version__   = '$Revision: 60982 $'[11:-2]

from zope.schema import SourceText
from zope.interface import Interface
from collective.gacontext import gacontextMessageFactory as _


class IGAContextMarker(Interface):
    """ a Marker interface
    """

class IGACode(Interface):
    """ The GA Form
    """
    ga_code = SourceText(
            title=_(u'JavaScript for web statistics support'),
            description=_(u"For enabling web statistics support "
                "from external providers (for e.g. Google "
                "Analytics). Paste the code snippets provided. "
                "It will be included in the rendered HTML as "
                "entered near the end of the page."),
            default=u'',
            required=False)

class IGAFinder(Interface):
    """ Finds the responsible GA Code for the context
    """
    def __call__(self, context):
        """ Returns the ga_code or none
        """

# vim: set ft=python ts=4 sw=4 expandtab :
