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
"""Keas Google Map Browser Views.

$Id: __init__.py 88883 2008-07-28 19:00:15Z pcardune $
"""

import zope.interface
from zope.pagetemplate.pagetemplatefile import PageTemplateFile
from zope.publisher.browser import BrowserView
from zope.schema.fieldproperty import FieldProperty
from zope.viewlet.viewlet import JavaScriptViewlet
from zope.publisher.interfaces.browser import IBrowserRequest

from keas.googlemap.geocode import Geocode
from keas.googlemap.browser import interfaces


class IGoogleMapBrowserLayer(IBrowserRequest):
    """GoogleMap Browser Layer."""


GoogleMapJavaScriptViewlet = JavaScriptViewlet('keas.googlemap.js')


class Marker(object):
    """Implementation of ``keas.googlemap.browser.interfaces.IMarker``."""
    zope.interface.implements(interfaces.IMarker)

    geocode = FieldProperty(interfaces.IMarker['geocode'])
    html = FieldProperty(interfaces.IMarker['html'])

    def __init__(self, geocode=None, html=u''):
        self.geocode = geocode or Geocode()
        self.html = html

    def __repr__(self):
        return '%s(%r, %r)' % (self.__class__.__name__,
                               self.geocode,
                               self.html)


class GoogleMap(object):
    """Implementation of ``keas.googlemap.browser.interfaces.IGoogleMap``."""

    zope.interface.implements(interfaces.IGoogleMap)

    template = PageTemplateFile("google-map.pt")
    id = FieldProperty(interfaces.IGoogleMap['id'])
    zoom = FieldProperty(interfaces.IGoogleMap['zoom'])
    type = FieldProperty(interfaces.IGoogleMap['type'])
    width = FieldProperty(interfaces.IGoogleMap['width'])
    height = FieldProperty(interfaces.IGoogleMap['height'])
    markers = FieldProperty(interfaces.IGoogleMap['markers'])

    @property
    def style(self):
        return u"width: %spx; height: %spx" % (self.width, self.height)

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        self.context = self.request = None

    def update(self):
        pass

    def render(self):
        return self.template(view=self)

    def javascript(self):
        markerString = '['
        for marker in self.markers:
            markerString += '{latitude:%s, longitude:%s, html:%s},' % (marker.geocode.latitude,
                                                                         marker.geocode.longitude,
                                                                         jsString(marker.html))
        markerString += ']'
        return """
          $(document).ready( function() {
               keas.googlemap.initialize({id:'%(id)s',
                                          zoom:%(zoom)s,
                                          type:%(type)s,
                                          markers:%(markers)s});} );
          $(document).unload( function() {GUnload();} );
          """ % dict(id=self.id,
                     zoom=self.zoom,
                     type=self.type,
                     markers=markerString)

def jsString(s):
    """Returns the string as a one line javascript representation."""
    if type(s) is unicode:
        return repr(s)[1:]
    return repr(s)


class GoogleMapBrowserView(BrowserView, GoogleMap):

    def __init__(self, context, request, **kwargs):
        BrowserView.__init__(self, context, request)
        GoogleMap.__init__(self, **kwargs)
