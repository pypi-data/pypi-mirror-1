twMaps.GMap = {
  description: 'ToscaWidgets Google Map',

  load_api: function (key, v) {
    try {
      var url = 'http://maps.google.com/maps?file=api&v=';
      var tag = ['<script src="', url, (v || '2'), '&key=', key,
                 '" type="text/javascript"></script>'].join('')
      document.write(tag);
      this.api_loaded = true;
    } catch (e) {
      this.api_loaded = false;
      throw new Error("Couldn't load Google Maps API: " + e.message);
    }
  },

  is_functional: function () {
    return (this.api_loaded && GBrowserIsCompatible());
  }
}

twMaps.GMap.Map = function () {
  this.initialize.apply(this, arguments);
};

twMaps.GMap.Map.prototype = twMaps.extend(new twMaps.Base.Map(), {
  superclass: twMaps.Base.Map.prototype,

  initialize: function (container_id, opts) {
    this.superclass.initialize.call(this, container_id, opts);
  },

  /**
   * @params opts An Object that may contain the following keys:
   *     ``center_y``
   *     ``center_x``
   *     ``zoom``
   */
  create_map: function (container, opts) {
	var self = this;
    var _create_map = function () {
      if (typeof(GMap2) == 'undefined') {
        setTimeout(_create_map, 1000);
        return;
      }
      var center_y = opts.center_y || 0;
      var center_x = opts.center_x || 0;
      var zoom = opts.zoom || 7;
      var width = opts.width || self.default_width;
      var height = opts.height || self.default_height;
      container.style.width = width;
      container.style.height = height;
      var map = new GMap2(container);
      map.setCenter(new GLatLng(center_y, center_x), zoom);
      // TODO: add opts for everything below
      map.addControl(new GLargeMapControl());
      map.addControl(new GMapTypeControl());
      map.addControl(new GScaleControl());
      map.addControl(new GOverviewMapControl());
      map.enableContinuousZoom();
      new GKeyboardHandler(map);
      self.map = map;
    }
    _create_map();
  },

  /* Events */

  add_listener: function (obj, signal, func) {
    GEvent.addListener(obj, signal, func);
  },

  on_unload: function () {
    GUnload();
  },

  /* Dimensions */

  set_size: function (dims) {
    // ``dims`` {w: <width>, h: <height>}
    this.superclass.set_size.call(this, dims);
    this.map.checkResize();
    this.map.setCenter(this.map.getCenter());
  },

  set_width: function (w) {
    this.set_size({w: w});
  },

  set_height: function (h) {
    this.set_size({h: h});
  },

  get_center: function () {
    var c = this.map.getCenter();
    return {x: c.lng(), y: c.lat()};
  },

  get_center_string: function () {
    var c = this.map.getCenter();
    var x = Math.round(c.lng() * 1000000) / 1000000;
    var y = Math.round(c.lat() * 1000000) / 1000000;
    return 'y' + ', ' + x;
  },

  set_center: function (center, zoom) {
    if (typeof(zoom) == 'undefined') {
      this.map.setCenter(new GLatLng(center.y, center.x));
    } else {
      this.map.setCenter(new GLatLng(center.y, center.x), zoom);
    }
  },

  set_zoom: function (zoom) {
    this.map.setZoom(zoom);
  },

  /* Overlays */

  add_overlay: function (overlay) {
    this.map.addOverlay(overlay);
  },

  remove_overlay: function (overlay) {
    this.map.removeOverlay(overlay);
  },

  draw_poly_line: function (points, color, weight, opacity) {
	var g_lat_lngs = [];
	for (p in points) {
	  g_lat_lngs(new GLatLng(point.y, point.x));
	}
    var line = new GPolyline(g_lat_lngs, color, weight, opacity);
    this.map.addOverlay(line);
    return line;
  },

  place_marker: function (point, icon) {
    var marker = new GMarker(new GLatLng(point.y, point.x), icon);
    this.map.addOverlay(marker);
    return marker;
  },

  place_markers: function (points, icons) {
    var markers = [];
    var len = points.length;
    if (icons) {
      for (var i = 0; i < len; ++i) {
        var p = points[i];
        var ll = new GLatLng(p.y, p.x);
        var marker = new GMarker(ll, {icon: icons[i]});
        markers.push(marker);
        this.map.addOverlay(marker);
      }
    } else {
      for (var i = 0; i < len; ++i) {
        var p = points[i];
        var ll = new GLatLng(p.y, p.x);
        var marker = new GMarker(ll);
        markers.push(marker);
        this.map.addOverlay(marker);
      }
    }
    return markers;
  },

  clear: function () {
    this.map.clearOverlays();
  },

  /* Bounds */

  center_and_zoom_to_bounds: function (bounds, center) {
    center = center || this.get_center_of_bounds(bounds);
    center = new GLatLng(center.y, center.x);
    var sw = bounds.sw;
    var ne = bounds.ne;
    var gbounds = new GLatLngBounds(new GLatLng(sw.y, sw.x),
                                    new GLatLng(ne.y, ne.x));
    this.map.setCenter(center, this.map.getBoundsZoomLevel(gbounds));
  },

  /* Info Window */

  open_info_window_html: function (point, html) {
    this.map.openInfoWindowHtml(new GLatLng(point.y, point.x), html);
  },

  close_info_window: function () {
    this.map.closeInfoWindow();
  },

  show_map_blowup: function (point) {
    this.map.showMapBlowup(new GLatLng(point.y, point.x));
  },

  /* Geocoding */

  _geocode: function (method, address, default_callback, callback, object) {
    this.geocoder = this.geocoder || new GClientGeocoder();
	if (!callback) {
	  object = this;
	  callback = default_callback;
	}
	if (object) {
	  bound_callback = function () {
		callback.apply(object, arguments);
	  }
	}
	this.geocoder[method](address, bound_callback || callback);
  },

  geocode_and_get_point: function (address, callback, object) {
    var default_cb = this._get_point_callback;
	this._geocode('getLatLng', address, default_cb, callback, object)
  },

  geocode_and_get_locations: function (address, callback, object) {
    var default_cb = this._get_locations_callback;
	this._geocode('getLocations', address, default_cb, callback, object)
  },

  _get_point_callback: function (g_lat_lng) {
	if (g_lat_lng) {
	  this.map.setCenter(g_lat_lng);
	  this.map.addOverlay(new GMarker(g_lat_lng));
	} else {
	  throw new Error('Address not found.');
	}
  },

  _get_locations_callback: function (locations) {

  }
});
