twMaps = {
  extend: function(destination, source) {
    for (var property in source) {
      destination[property] = source[property];
    }
    return destination;
  }
};


twMaps.Base = {
    description: 'ToscaWidgets Base Map',
    load_api: function () {},
    is_functional: function () { return true; }
};


twMaps.Base.Map = function () {
  this.initialize.apply(this, arguments);
};

twMaps.Base.Map.prototype = {
  default_width: '400px',
  default_height: '400px',

  /**
   * @param container_id ID of element that contains this map
   */
  initialize: function (container_id, opts) {
    if (arguments.length == 0) return;
    opts = opts || {};
    this.container = document.getElementById(container_id);
    this.create_map(document.getElementById(container_id), opts);
  },

  create_map: function (container, opts) {
    var map = document.createElement('div');
    var width = opts.width || this.default_width;
    var height = opts.height || this.default_height;
    container.style.width = width;
    container.style.height = height;
    map.style.height = '100%';
    map.style.overflow = 'auto';
    container.appendChild(map);
    this.map = map;
    this._put('twMaps Base Map');
  },

  _put: function (content) {
    var div = document.createElement('div');
    div.innerHTML = '#' + (this._put_count = (this._put_count || 1)) + ' ' +
                    content;
    this._put_count += 1;
    this.map.appendChild(div);
    return div;
  },

  clear: function () {
    this.map.innerHTML = '';
  },

  set_size: function (dims) {
    if (typeof(dims.w) != 'undefined') {
      this.container.style.width = dims.w;
    }
    if (typeof(dims.h) != 'undefined') {
      this.container.style.height = dims.h;
    }
  },

  set_width: function (width) {
    this.container.style.width = width;
  },

  set_height: function (height) {
    this.container.style.height = height;
  },

  on_unload: function () {
    document.body.innerHTML = 'Bye.';
  },

  get_center: function () {
    return {x: 0, y: 0};
  },

  get_center_string: function () {
    var c = this.get_center();
    var x = Math.round(c.x * 1000000) / 1000000;
    var y = Math.round(c.y * 1000000) / 1000000;
    return ["longitude=", x, ", ", "latitude=", y].join('');
  },

  set_center: function (center, zoom) {
    this._put(['Set Center: ', center.x, ', ', center.y,
              (zoom ? '; Zoom: ' + zoom : '')].join(''));
  },

  set_zoom: function (zoom) {
    this.map.innerHTML += ('<br/>New zoom level: ' + zoom);
  },

  open_info_window_html: function (point, html) {},

  close_info_window: function () {},

  show_map_blowup: function (point) {
    var content = 'Map blowup: ' + point.x + ', ' + point.y;
    this._put(content);
  },

  add_overlay: function (overlay) {
    var content = 'Added Overlay: ' + overlay.toString();
    return this._put(content);
  },

  remove_overlay: function (overlay) {
    var content = 'Removed Overlay: ' + overlay.toString();
    this._put(content);
  },

  draw_poly_line: function (points, color, weight, opacity) {
    var line = {
      type: 'PolyLine',
      toString: function () {
        return this.type;
      }
    };
    return this.add_overlay(line);
  },

  place_marker: function (point, icon) {
    var marker = {
      type: 'Marker',
      x: point.x,
      y: point.y,
      toString: function () {
        return [this.type, ' at ', this.x, ', ', this.y].join('');
      }
    };
    return this.add_overlay(marker);
  },

  /**
   * Put some markers on the map
   * @param points An array of points
   * @param icons An array of icons (optional)
   * @return An array of the markers added
   */
  place_markers: function (points, icons) {
    var markers = [];
    var len = points.length;
    for (var i = 0; i < len; ++i) {
      p = points[i];
      var marker = this.place_marker(p);
      markers.push(marker);
    }
    return markers;
  },


  /* Bounds */

  get_bounds_for_points: function (points) {
    var xs = [];
    var ys = [];
    for (var i = 0; i < points.length; ++i) {
      var p = points[i];
      xs.push(p.x);
      ys.push(p.y);
    }
    var comp = function (a, b) { return a - b; };
    xs.sort(comp);
    ys.sort(comp);
    var bounds = {
      sw: {x: xs[0], y: ys[0]},
      ne: {x: xs.pop(), y: ys.pop()}
    };
    return bounds;
  },

  /**
   * @param bounds A set of points representing a bounding box (sw, ne)
   * @return Center of bounding box {x: x, y: y}
   */
  get_center_of_bounds: function (bounds) {
    var sw = bounds.sw;
    var ne = bounds.ne;
    return {x: (sw.x + ne.x) / 2.0, y: (sw.y + ne.y) / 2.0};
  },

  center_and_zoom_to_bounds: function (bounds, center) {},

  add_listener: function (obj, signal, func) {}
};

