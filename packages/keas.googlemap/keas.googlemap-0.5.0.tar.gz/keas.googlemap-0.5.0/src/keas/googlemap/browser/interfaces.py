##############################################################################
#
# Copyright (c) 2007 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Keas Google Map Interfaces.

$Id: interfaces.py 88883 2008-07-28 19:00:15Z pcardune $
"""
import zope.interface
import zope.schema

from keas.googlemap.interfaces import IGeocode

NORMAL_MAP = u'G_NORMAL_MAP'
SATELLITE_MAP = u'G_SATELLITE_MAP'
HYBRID_MAP = u'G_HYBRID_MAP'

class IGoogleMap(zope.interface.Interface):
    """An Interface for static google maps."""

    id = zope.schema.TextLine(
        title=u"ID for the google map html tag",
        required=True,
        default=u'google-map')

    zoom = zope.schema.Choice(
        title=u"Zoom",
        default=1,
        values=range(20),
        required=True)

    type = zope.schema.Choice(
        title=u"Type",
        values=(NORMAL_MAP, SATELLITE_MAP, HYBRID_MAP),
        default=NORMAL_MAP,
        required=True)

    markers = zope.schema.List(
        title=u'Markers',
        default=[],
        required=True)

    width = zope.schema.Int(
        title=u'Width in px',
        default=500,
        required=True)

    height = zope.schema.Int(
        title=u'Height in px',
        default=400,
        required=True)


class IMarker(zope.interface.Interface):
    """An interface for a map marker."""

    geocode = zope.schema.Object(
        title=u'Geocode',
        schema=IGeocode,
        required=True)

    html = zope.schema.Text(
        title=u'html',
        description=u'HTML that goes inside the marker popup.',
        required=False)
