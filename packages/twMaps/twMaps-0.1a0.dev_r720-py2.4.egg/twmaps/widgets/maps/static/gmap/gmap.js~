twGMap = (function () {
  var api_url = 'http://maps.google.com/maps?file=api&amp;v=2&amp;key=';

  function $(id) {
    return document.getElementById(id);
  }

  return {
    load_api: function (api_key) {
      document.write('<script src="' + api_url + api_key +
                     '" type="text/javascript"></script>');
    },

    create_map: function(container_id, opts) {
      // We need this to close over ``container_id`` and ``opts``
      var _create_map = function () {
        if (typeof(GMap2) == 'undefined') {
          setTimeout(_create_map, 1000);
          return;
        }
        var container = $(container_id);
        var map = new GMap2(container);
        y = opts.y || 0;
        x = opts.x || 0;
        zoom = opts.zoom || 7;
        map.setCenter(new GLatLng(y, x), zoom);
        // TODO: add opts for everything below
        map.addControl(new GLargeMapControl());
        map.addControl(new GMapTypeControl());
        map.addControl(new GScaleControl());
        map.addControl(new GOverviewMapControl());
        map.enableContinuousZoom();
        new GKeyboardHandler(map);
        this.map = map;
      }
    }
  }
})();
