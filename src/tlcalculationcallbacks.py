import tlconfiguration
import pandas as pd

class CalculationCallbacks:
    def __init__(self, data_source, log_data, result, fields):
        self.data_sources = data_source
        self.log_data = log_data
        self. result = result
        self.fields = fields

    def calculation_button_clicked(self):
        if (self.fields.control_field.calculation_checkbox.active and
                self.result.update.status.borehole_id != '' and
                self.result.update.status.selected_sample != tlconfiguration.selected_sample_initial):

            profile_name = self.result.update.status.borehole_id + '_' + str(self.result.update.status.selected_sample)
            if "." in profile_name:
                profile_name = profile_name.split(".")[0]

            profile = self.log_data.profiles[profile_name]
            self.result.calculation.execute(profile)

            self.result.update_calculation()
            self.data_sources.update_calculation()

    def calculation_checkbox_changed(self, attr, old, new):
        self.data_sources.update_calculation()

    def delete_calc_button_clicked(self):
        columns = ['calc_bottom_point', 'calc_gradient']
        for col in columns:
            self.result.update.update_fitting(col, pd.NA)

        self.data_sources.update_calculation()