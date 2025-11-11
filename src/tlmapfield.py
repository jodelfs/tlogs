from tlmapplot import MapPlot

from bokeh.models import Button, RadioGroup
from bokeh.layouts import row, column

class MapField:
    def __init__(self, data_sources, infos_unique):
        self.map_plot = MapPlot(data_sources, infos_unique)

        self.reset_button = Button(label="Reset Map", button_type="warning")
        self.background_selection = RadioGroup(active=0, labels=["No background", "DEM"])


    def field(self):
        row1 = row([self.reset_button, self.background_selection])
        return column([row1,
                       self.map_plot.p])