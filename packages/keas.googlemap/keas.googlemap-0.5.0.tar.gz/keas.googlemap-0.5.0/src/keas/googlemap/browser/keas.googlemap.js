var keas = keas || {};
keas.googlemap = {
    initialize: function(config){
        /*config is of the form
          {id: "some-dom-element-id",
          zoom: 12, //the desired zoom level,
          type: G_NORMAL_MAP, //a google maps map type string.
          markers: [{latitude: 3.1234,
                     longitude: 4.52342,
                     html: "stuff that appears in the window"}]} //an array of markers.
        */
        if (GBrowserIsCompatible()) {
            var center;
            if (config.markers.length > 0){
                center = new GLatLng(config.markers[0].latitude,
                                     config.markers[0].longitude);
                    }
            else {
                center = new GLatLng(0.0, 0.0);
            }
            var map = new GMap2(document.getElementById(config.id));

            map.addControl(new GLargeMapControl());
            map.addControl(new GMapTypeControl());
            map.setCenter(center, config.zoom, config.type);
            var bounds = map.getBounds();
            var mgr = new MarkerManager(map);
            var markers = [];
            for (var i=0; i < config.markers.length; i++){
                var conf = config.markers[i];
                var marker = new GMarker(new GLatLng(conf.latitude, conf.longitude));
                marker.bindInfoWindowHtml(conf.html);
                markers.push(marker);
                bounds.extend(marker.getPoint());
            }

            mgr.addMarkers(markers, 0);
            map.setZoom(map.getBoundsZoomLevel(bounds));
            map.setCenter(bounds.getCenter());

            mgr.refresh();
        }
    }
};