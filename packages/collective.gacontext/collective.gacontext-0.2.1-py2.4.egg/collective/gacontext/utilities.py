# -*- coding: utf-8 -*-
#
# File: utilities.py
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

from Acquisition import aq_inner,  aq_parent
from collective.gacontext.interfaces import *

def _chain(object):
    """Generator to walk the acquistion chain of object, considering that it
    could be a function.
    """
    # original code from the optilux example

    # Walk up the acquisition chain of the object, to be able to check
    # each one for IWorkspace.

    # If the thing we are accessing is actually a bound method on an
    # instance, then after we've checked the method itself, get the
    # instance it's bound to using im_self, so that we can continue to 
    # walk up the acquistion chain from it (incidentally, this is why we 
    # can't juse use aq_chain()).

    context = aq_inner(object)

    while context is not None:
        yield context

        func_object = getattr(context, 'im_self', None )
        if func_object is not None:
            context = aq_inner(func_object)
        else:
            # Don't use aq_inner() since portal_factory (and probably other)
            # things, depends on being able to wrap itself in a fake context.
            context = aq_parent(context)

def gafinder(context):
    """ find the ga snippet responsible for the context
    """
    for obj in _chain(context):
        if IGAContextMarker.providedBy(obj):
            return IGACode(obj).ga_code
    return None

# vim: set ft=python ts=4 sw=4 expandtab :
