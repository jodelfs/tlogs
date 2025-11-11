from bokeh.layouts import row, column
from bokeh.models import (Spinner, Checkbox,AutocompleteInput, Slider,
                          Select, Button, RangeSlider, Spacer, Div, RadioGroup)
import pandas as pd
import tlconfiguration
from tllogger import logger

class ControlField:
    def __init__(self, infos_unique, result, log_data):

        self.result = result
        self.log_data = log_data

        #selection
        self.borehole = AutocompleteInput(title="Select borehole",
                                          completions=list(infos_unique['borehole_id']),
                                          min_characters=1)
        self.sample = Select(title="Select sample:", value="0", options=["0"])

        #quality field
        self.quality = Spinner(title="Log quality", low=-1, high=3, step=1, value=None)
        self.drilling_induced = Checkbox(label="Drilling Induced", active=False)
        self.deactivated = Checkbox(label="Deactivate", active=False)

        # point field
        self.delete_point = Button(label="Delete point", button_type="danger")
        self.delete_all_points = Button(label="Delete all pnts", button_type="danger")
        self.attach_to_sample = Checkbox(label="Attach to sample", active=True)

        # profile calculation
        self.calculation_button = Button(label="Update calc..", button_type="success")
        self.calculation_checkbox = Checkbox(label="Calculation", active=False)

        # profile fit
        self.fit_slider = RangeSlider(start=0, end=1, value=(0, 0), step=1, title="Fit range")
        self.fit_button = Button(label="Update fit", button_type="success")
        self.fit_checkbox = Checkbox(label="Profile fit", active=False)
        self.fit_result_text = Div(text='', width=200, height=10)

        self.delete_fit_button = Button(label="Del fit", button_type="danger")
        self.delete_calc_button = Button(label="Del calc.", button_type="danger")

        #
        self.flow_info_slider = Slider(start=0, end=4, value=1, step=1, title='Flow info')
        self.time_info_slider = Slider(start=0, end=4, value=1, step=1, title='Time info')
        self.borehole_info_slider = Slider(start=0, end=3, value=1, step=1, title='Borehole info')
        self.lithology_info_slider = Slider(start=0, end=2, value=0, step=1, title='lithology info')

        self.method_selection = RadioGroup(active=0, labels=['Profile', 'Calculation', 'Fit'])

    def update_fit_slider(self):
        logger.debug('Field update - Fit-slider')
        if (self.fit_checkbox.active and
                self.result.update.status.borehole_id != '' and
                self.result.update.status.selected_sample != tlconfiguration.selected_sample_initial):

            profile_name = str(self.result.update.status.borehole_id) + '_' + str(
                self.result.update.status.selected_sample)
            if "." in profile_name:
                profile_name = profile_name.split(".")[0]

            slider_range= (int(self.log_data.profiles[profile_name]['z'].min()),
                           int(self.log_data.profiles[profile_name]['z'].max()) + 1)

            self.fit_slider.start = slider_range[0]
            self.fit_slider.end = slider_range[1]

            value_stored = self.result.fitting.loc[self.result.fitting[
                                        'borehole_id'] == self.result.update.status.borehole_id, 'fit_m'].values[0]

            if pd.isna(value_stored):  # no stored fit results
                self.fit_slider.value = slider_range
            else:
                self.fit_slider.value = self.result.fit.depth_range

        else:  # not active
            self.fit_slider.value = (0, 0)
            self.fit_slider.start = 0
            self.fit_slider.end = 1

    def field(self):
        #row_checkboxes = row([self.deactivated, self.drilling_induced])
        col1 = column([self.borehole, self.sample])
        col2 = column([self.quality, self.drilling_induced, self.deactivated])
        col3 = column([self.attach_to_sample, self.delete_all_points, self.delete_point])
        col4 = column([Spacer(height=50), self.calculation_checkbox, self.fit_checkbox])

        col1_info = column([self.flow_info_slider, self.time_info_slider,
                            self.borehole_info_slider, self.lithology_info_slider])

        row1 = row([self.method_selection, col1_info])
        row2 = row([self.calculation_button, self.delete_calc_button, Spacer(width=130), self.fit_result_text])
        row3 = row([self.fit_button, self.delete_fit_button, Spacer(width=10), self.fit_slider])
        col5 = column([Spacer(height=20), row1, row2, row3])


        return row([col1, col2, col3, col4, col5])