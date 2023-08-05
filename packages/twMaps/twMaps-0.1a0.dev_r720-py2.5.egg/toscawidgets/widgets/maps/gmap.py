from toscawidgets.api import Widget, CSSLink, JSLink, js_function

__all__ = ['GMap']


twgmap_css = CSSLink(modname=__name__, filename='static/gmap/gmap.css',
                     media='screen')
twmap_js = JSLink(modname=__name__, filename='static/map/map.js')
twgmap_js = JSLink(modname=__name__, filename='static/gmap/gmap.js',
                   javascript=[twmap_js])


class GMap(Widget):
    params = ['css_class', 'map_opts']
    css_class = 'twmaps-gmap'
    map_opts = {
        'api_key': None, 
        'center_y': 0, 
        'center_x': 0, 
        'zoom': 14,
        'width': '400px',
        'height': '400px'
    }
    template = '<div id="${id}" class="${css_class}"></div>'
    css = [twgmap_css]
    javascript = [twgmap_js]
    include_dynamic_js_calls = True

    def __init__(self, id=None, parent=None, children=[], **kw):
        self.map_opts.update(kw.get('map_opts', {}))
        key = self.map_opts['api_key']
        self.add_call('twMaps.GMap.load_api("%s");' % key)
        super(GMap, self).__init__(id, parent, children, **kw)

    def update_params(self, d):
        super(GMap, self).update_params(d)
        # Use initial map opts as base...
        map_opts = self.map_opts.copy()
        # ...then update with map opts in ``d``
        map_opts.update(d.get('map_opts', {}))
        for k in map_opts:
            try: v = float(map_opts[k])
            except: pass
            else: map_opts[k] = v
        new_map = js_function('var %s = new twMaps.GMap.Map' % self.id)
        self.add_call(new_map(self.id, map_opts))


if __name__ == '__main__':
    m = GMap('twgmap')
    m.update_params({})
    m.update_params(dict(map_opts={'x': 1}))
    m.update_params(dict(map_opts={'x': '1'}))
    print m.display()
