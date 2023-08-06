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

$Id: __init__.py 92829 2008-11-07 10:14:30Z nadako $
"""

import zope.interface
import zope.component
from zope.pagetemplate.pagetemplatefile import PageTemplateFile
from zope.publisher.browser import BrowserView
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.schema.fieldproperty import FieldProperty
from zope.viewlet.viewlet import JavaScriptViewlet
from zope.viewlet.viewlet import ViewletBase

from keas.googlemap.geocode import Geocode
from keas.googlemap.browser import interfaces
from keas.googlemap import jsoncompat as json


class IGoogleMapBrowserLayer(IBrowserRequest):
    """GoogleMap Browser Layer."""


GoogleMapJavaScriptViewlet = JavaScriptViewlet('keas.googlemap.js')
GoogleMapMarkersViewletLocal = JavaScriptViewlet('markermanager.js')

class GoogleMapMarkersViewlet(ViewletBase):

    def render(self):
        return ('<script type="text/javascript" '
                'src="http://gmaps-utility-library.googlecode.com'
                '/svn/trunk/markermanager/release/src/markermanager.js">'
                '</script>')


class Marker(object):
    """Implementation of ``keas.googlemap.browser.interfaces.IMarker``."""
    zope.interface.implements(interfaces.IMarker)

    geocode = FieldProperty(interfaces.IMarker['geocode'])
    html = FieldProperty(interfaces.IMarker['html'])
    popupOnLoad = FieldProperty(interfaces.IMarker['popupOnLoad'])

    def __init__(self, geocode=None, html=u'', popupOnLoad=False):
        self.geocode = geocode or Geocode()
        self.html = html
        self.popupOnLoad = popupOnLoad

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
    controls = FieldProperty(interfaces.IGoogleMap['controls'])
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
        markers = []
        popup_marker = None
        for i, marker in enumerate(self.markers):
            if marker.popupOnLoad:
                if popup_marker is not None:
                    raise ValueError('Only one marker can have popup on load at the same time')
                else:
                    popup_marker = i
            markers.append(dict(latitude=marker.geocode.latitude,
                                longitude=marker.geocode.longitude,
                                html=marker.html))
        markerString = json.encode(markers)
        return """
          var keas_googlemap_maploader = function(){
               keas.googlemap.initialize({id:'%(id)s',
                                          zoom:%(zoom)s,
                                          type:%(type)s,
                                          controls:%(controls)s,
                                          popup_marker:%(popup_marker)s,
                                          markers:%(markers)s});
          };
          $(document).unload( function() {GUnload();} );
          """ % dict(id=self.id,
                     zoom=self.zoom,
                     type=self.type,
                     controls=json.encode(self.controls),
                     popup_marker=json.encode(popup_marker),
                     markers=markerString)

class GoogleMapBrowserView(BrowserView, GoogleMap):

    def __init__(self, context, request, **kwargs):
        BrowserView.__init__(self, context, request)
        GoogleMap.__init__(self, **kwargs)
