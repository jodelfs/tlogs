from scipy.optimize import curve_fit
from math import sqrt
import numpy as np
import pandas as pd

def linear_function(depth, m, c):
    return m * depth + c


class Fit:

    param = [np.nan, np.nan] # Floats, m: param[0], c: param[1]
    param_cov = [[np.nan, np.nan] , [np.nan, np.nan] ] # std_m: sqrt(param_cov[0][0]), std_c = sqrt(param_cov[1][1])

    depth_range = [np.nan, np.nan] # top, bottom
    T_depth_range = [np.nan, np.nan]

    fit_slider =  None # value: range
    text_field = None

    def __init__(self, result, log_data):
        self.fitting = result.fitting

    def set_fields(self, fields):
        self.fit_slider = fields.control_field.fit_slider
        self.text_field = fields.control_field.fit_result_text

    def get_depth_range(self):
        return self.depth_range

    def update_for_borehole(self, borehole_id):

        self.param[0] = self.fitting.fillna(np.nan).loc[self.fitting.fillna(np.nan)['borehole_id'] == borehole_id, 'fit_m'].values[0]
        self.param[1] = self.fitting.fillna(np.nan).loc[self.fitting.fillna(np.nan)['borehole_id'] == borehole_id, 'fit_c'].values[0]
        self.param_cov[0][0] = self.fitting.fillna(np.nan).loc[self.fitting.fillna(np.nan)['borehole_id'] == borehole_id, 'fit_std_m'].values[0]
        self.param_cov[1][1] = self.fitting.fillna(np.nan).loc[self.fitting.fillna(np.nan)['borehole_id'] == borehole_id, 'fit_std_c'].values[0]

        self.depth_range = [self.fitting.fillna(np.nan).loc[self.fitting.fillna(np.nan)['borehole_id'] == borehole_id, 'fit_depth_top'].values[0],
                            self.fitting.fillna(np.nan).loc[self.fitting.fillna(np.nan)['borehole_id'] == borehole_id, 'fit_depth_bottom'].values[0]]

        try:
            self.T_depth_range = linear_function(np.array(self.depth_range), self.param[0], self.param[1])
        except:
            self.T_depth_range = [pd.NA, pd.NA]

        self.text_field.text = 'c: {:.2f} ({:.3f})<br>m: {:.3f} ({:.4f})'.format(
            self.param[1], self.param_cov[1][1], self.param[0], self.param_cov[0][0])

    def get_result(self):
        return self.param, self.param_cov

    def execute(self, profile):
        self.depth_range = self.fit_slider.value

        valid_indices = (profile.z >= self.depth_range[0]) & (profile.z <= self.depth_range[1])
        z_clipped = profile.z[valid_indices]
        T_clipped = profile['T'][valid_indices]

        self.param, self.param_cov = curve_fit(linear_function, z_clipped, T_clipped)

        self.T_depth_range = linear_function(np.array(self.depth_range), self.param[0], self.param[1])

        self.text_field.text = 'c: {:.2f} ({:.3f})<br>m: {:.3f} ({:.4f})'.format(
            self.param[1], self.param_cov[1][1], self.param[0], self.param_cov[0][0])






