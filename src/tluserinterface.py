from bokeh.layouts import gridplot

from tlimport import Import
from tlFields import Fields

from tldatasources import DataSources
from tlevents import Events

class UserInterface:

    def __init__(self):
        _import = Import()
        log_data, infos_unique, result = _import.read_data()
        data_sources = DataSources(log_data, infos_unique, result)
        self.fields = Fields(data_sources, infos_unique, log_data, result)
        data_sources.set_fields(self.fields)
        result.points.set_fields(self.fields)
        result.fit.set_fields(self.fields)
        result.calculation.set_fields(self.fields)

        callbacks = Events(data_sources, log_data, infos_unique, result, self.fields)


    def layout(self):
        return gridplot([[self.fields.control_field.field()],
                         [self.fields.map_field.field()
                          , self.fields.log_field.field()
                           , self.fields.note_field.field()
                          ]])#, sizing_mode="scale_width")