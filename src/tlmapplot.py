from bokeh.plotting import figure
from bokeh.models import (LinearColorMapper, ColorBar,
                          Toolbar, HoverTool, TapTool, PanTool, BoxZoomTool, WheelZoomTool)
from bokeh.palettes import RdYlGn

import tlconfiguration
import tlproject
from tldem import DEM

import numpy as np
from tllogger import logger

class MapPlot:
    def __init__(self, data_sources, infos_unique):

        self.p = figure(title="{} boreholes".format(
            len(list(infos_unique['borehole_id']))
            ), # number of boreholes
       #active_drag="pan",  # Standardbewegung: Verschieben
       #active_scroll="wheel_zoom",  # Standard-Zoom: Mausrad
       width=400,  # match_aspect=True,
        #x_range=(300000, 400000), y_range=(5500000, 5600000)
        #tools = 'tap'
       )

        self.data_sources = data_sources

        self.p.background_fill_color = None  # Hintergrund wirklich transparent machen
        self.p.border_fill_color = None

        self.dem = DEM(infos_unique)

        color_mapper = LinearColorMapper(palette=RdYlGn[int((tlproject.dem_range[1]-tlproject.dem_range[0]) / 100)], low=tlproject.dem_range[0], high=tlproject.dem_range[1])

        self.background_image = self.p.image(image='image', x='x', y='y', dw='dw', dh='dh',
                                             source=data_sources.map_background, color_mapper=color_mapper)

        self.background_color_bar = ColorBar(color_mapper=color_mapper, label_standoff=12, location=(0, 0),
                             title="Elevation [m]")
        self.background_color_bar.major_label_text_font_size = "12pt"
        self.background_color_bar.title_text_font_size = "14pt"
        self.p.add_layout(self.background_color_bar, 'below')


        self.p.toolbar = Toolbar(tools=[TapTool(), PanTool(), BoxZoomTool(), WheelZoomTool()])
        self.p.toolbar.logo = None
        #self.p.toolbar_location = "above"

        colors = ['black', 'red', 'blue', 'yellow', 'grey'] # colors for quality levels

        self.p.scatter('x', 'y', source=data_sources.map_boreholes, size=8, color="black")

        for ndx, quality in enumerate(tlconfiguration.log_qualities):
            self.p.scatter('x', 'y', source=data_sources.map_boreholes_quality[quality], size=5, color=colors[ndx])
        self.p.scatter('x', 'y', source=data_sources.map_boreholes_drillingInduced, size=2, color='black')

        self.p.scatter('x', 'y', source=data_sources.map_boreholes, size=10, alpha=0, hover_alpha=0., color=None)

        self.p.scatter('x', 'y', source=data_sources.map_borehole_selected, size=10, color="black")#, marker='cross')
        self.p.scatter('x', 'y', source=data_sources.map_borehole_selected, size=6, color="orange")  # , marker='cross')

        self.p.xaxis.axis_label = "UTM Easting (m)"  # X-Achsentitel
        self.p.yaxis.axis_label = "UTM Northing (m)"  # Y-Achsentitel

        hover = HoverTool(
            tooltips=[("Borehole ID", "@bh_id")],  # Zeigt Bohrröhren-ID an
            mode="mouse"
        )
        self.p.add_tools(hover)

    def update_background(self, value):
        logger.debug('Update map background: ' + str(value))
        if value == 0:
            no_dem = np.zeros((10, 10))
            image_data = np.where(no_dem == 0, np.nan, no_dem)


            self.data_sources.map_background.data={ 'image':[image_data],#  [np.flipud(dem.matrix)],
                                                      'x': [self.dem.extent[0]], 'y': [self.dem.extent[2]],
                                                      'dw': [self.dem.extent[1] - self.dem.extent[0]],
                                                      'dh': [self.dem.extent[3] - self.dem.extent[2]] }
        elif value == 1:
            self.data_sources.map_background.data={ 'image':[np.flipud(self.dem.matrix) ],#  [np.flipud(dem.matrix)],
                                                      'x': [self.dem.extent[0]], 'y': [self.dem.extent[2]],
                                                      'dw': [self.dem.extent[1] - self.dem.extent[0]],
                                                      'dh': [self.dem.extent[3] - self.dem.extent[2]] }


    #def field(self):
    #    return column([self.p])

