from tllogfield import LogField
from tlmapfield import MapField
from tlnotefield import NoteField
from tlcontrolfield import ControlField

from tllogger import logger

class Fields:
    def __init__(self, data_sources, infos_unique, log_data, result):
        self.result = result

        self.map_field = MapField(data_sources, infos_unique)
        self.log_field = LogField(data_sources, log_data, result, self)

        self.control_field = ControlField(infos_unique, result, log_data)

        self.note_field = NoteField(data_sources, result, log_data, self.log_field.log_plot)

    def update_for_borehole(self):
        self.control_field.sample.options = ["0"] + list(map(str, self.result.update.status.sample_list))  # unt to str

        selected_sample = self.result.get_field_value_for_borehole('selected_sample')
        selected_sample = str(int(selected_sample)) if isinstance(selected_sample, float) else str(selected_sample)
        self.control_field.sample.value = selected_sample
        print("selected: ", selected_sample)
        self.control_field.drilling_induced.active = self.result.get_field_value_for_borehole('drillingInduced')
        self.control_field.deactivated.active = self.result.get_field_value_for_borehole('deactivated')
        self.control_field.quality.value = self.result.get_field_value_for_borehole('quality')

        self.control_field.flow_info_slider.value = self.result.get_field_value_for_borehole('flow_info')
        self.control_field.time_info_slider.value = self.result.get_field_value_for_borehole('time_info')
        self.control_field.borehole_info_slider.value = self.result.get_field_value_for_borehole('borehole_info')
        self.control_field.lithology_info_slider.value = self.result.get_field_value_for_borehole('lithology_info')

        self.control_field.update_fit_slider()
        self.note_field.update_for_borehole()

        self.log_field.log_plot.update()


