from toscawidgets.api import Widget, CSSLink, JSLink

__all__ = ['GMap']


twgmap_css = CSSLink(modname=__name__, filename='static/gmap/gmap.css',
                     media='screen')
twgmap_js = JSLink(modname=__name__, filename='static/gmap/gmap.js')


class GMap(Widget):
    map_params = ['api_key', 'css_class', 'x', 'y', 'zoom']
    params = map_params
    template = '<div id="${id}" class="${css_class}"></div>'
    css = [twgmap_css]
    javascript = [twgmap_js]
    include_dynamic_js_calls = True

    def update_params(self, d):
        super(GMap, self).update_params(d)
        self.add_call('twGMap.load_api("%s");' % self.api_key)
        opts = {}
        for p in self.map_params:
            val = getattr(self, p, None)
            if val is not None:
                try:
                    val = float(val)
                except (ValueError, TypeError):
                    pass
                opts[p] = val
        self.add_call('twGMap.create_map("%s", %s);' % (self.id, opts))
