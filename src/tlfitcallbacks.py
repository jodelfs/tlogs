from tllogger import logger
import tlconfiguration
import pandas as pd

class FitCallbacks:
    def __init__(self, data_source, log_data, result, fields):
        self.data_sources = data_source
        self.log_data = log_data
        self.result = result
        self.fields = fields

    def fit_checkbox_changed(self, attr, old, new):
        self.fields.control_field.update_fit_slider()
        self.data_sources.update_fit()

    def update_fit_range(self, attr, old, new):
        if new:
            logger.debug('Field update - Fit range: ' + str(new[0]) + ' ' + str(new[1]))
            self.data_sources.fit_range.data['z'] = [[new[0], new[0]], [new[1], new[1]]]

    def fit_button_clicked(self):
        if (self.fields.control_field.fit_checkbox.active and
                self.result.update.status.borehole_id != '' and
                self.result.update.status.selected_sample != tlconfiguration.selected_sample_initial):

            profile_name = self.result.update.status.borehole_id + '_' + str(
                self.result.update.status.selected_sample)

            if "." in profile_name:
                profile_name = profile_name.split(".")[0]

            profile = self.log_data.profiles[profile_name]

            self.result.fit.execute(profile)

            self.result.update_fit()
            self.data_sources.update_fit()

    def delete_fit_button_clicked(self):
        columns = ['fit_m', 'fit_c', 'fit_std_m', 'fit_std_c', 'fit_depth_top', 'fit_depth_bottom']
        for col in columns:
            self.result.update.update_fitting(col, pd.NA)

        self.data_sources.update_fit()


