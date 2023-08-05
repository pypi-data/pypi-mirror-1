from twmapssampleapppylons.lib.base import *

# TW
from toscawidgets.mods.pylonshf import render_response
from toscawidgets.api import Widget, WidgetBunch

from toscawidgets.widgets.maps import gmap


class MapsController(BaseController):
    def __before__(self):
        config = request.environ.get('paste.config')
        self.map_opts = {
            'api_key': config['twMaps.gmap.api_key'],
            'zoom': config.get('twMaps.gmap.zoom', 14),
            'center_y': config.get('twMaps.center_y', 0),
            'center_x': config.get('twMaps.center_x', 0),
            'width': config.get('twMaps.width', '400px'),
            'height': config.get('twMaps.height', '400px'),
        }

    def index(self):
        c.w = WidgetBunch()
        c.w.gmap = gmap.GMap('twgmap', map_opts=self.map_opts)
        c.title = 'Sample twMaps App'
        return render_response('/map.html')