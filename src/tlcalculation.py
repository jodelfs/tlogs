
import numpy as np
import pandas as pd

import tlconfiguration
from tlmath import calculate_inflow_rate

def int_if_floatstr(value):
    try:
        if isinstance(value, str) and float(value).is_integer():
            return int(float(value))
    except ValueError:
        pass

    return value

class Calculation:
    note_field = None
    calculation_checkbox = None

    z = []
    T_geothermal = []
    T_borehole_calculated = []

    bottom_point = str()
    average_gradient = pd.NA

    def __init__(self, result, log_data):
        self.result = result
        self.log_data = log_data

    def set_fields(self, fields):
        self.note_field = fields.note_field
        self.calculation_checkbox = fields.control_field.calculation_checkbox

    def get_depth_range(self):
        return [0, 0]

    def get_result(self):
        return self.bottom_point, self.average_gradient

    def update_for_borehole(self, borehole_id):
        value_stored = self.result.fitting.loc[self.result.fitting[
                                                   'borehole_id'] == self.result.update.status.borehole_id, 'calc_gradient'].values[0]

        if (self.calculation_checkbox and not pd.isna(value_stored) and self.result.update.status.borehole_id != '' and
                self.result.update.status.selected_sample != tlconfiguration.selected_sample_initial):

            profile = self.log_data.profiles[
                str(self.result.update.status.borehole_id) + '_' + str(int_if_floatstr(self.result.update.status.selected_sample))]
            self.execute(profile)

    def execute(self, profile):
        (inflow_amounts, gradient_geothermal,
         conductance_thermal, correction_thermal) = self.note_field.get_input_for_calculation()
        try:
            gradient_z_range = list(gradient_geothermal.keys())
            z_min_ranges, z_max_ranges = gradient_z_range[-1][0], gradient_z_range[0][1]

            profile_z_min, profile_z_max = (int(profile['z'].min())+1,
                            int(profile['z'].max()))

            z_min_calc, z_max_calc = max(z_min_ranges, profile_z_min), min(z_max_ranges, profile_z_max)

            self.z = np.arange(z_min_calc, z_max_calc+1)
            T = np.interp(self.z, profile['z'], profile['T']) # to get bottom value

            dz = 1
            q_in = calculate_inflow_rate(z_min_calc, z_max_calc, inflow_amounts)  # check boundaries min, max!!!
            self.average_gradient = 0
            total_z_range = 0

            self.T_geothermal = np.full(self.z.size, np.nan)

            T_bottom = T[-1] + correction_thermal
            self.T_geothermal[-1] = float(T_bottom)
            for height in gradient_z_range:
                gradient_z_min = height[0]
                gradient_z_max = height[1]

                z_min = max(profile_z_min, gradient_z_min)
                z_max = min(profile_z_max, gradient_z_max)

                gradient = float(gradient_geothermal[height])

                self.average_gradient += gradient * (z_max - z_min)
                total_z_range += z_max - z_min
                for _z in range(z_min, z_max):
                    self.T_geothermal[_z-z_min_calc] = self.T_geothermal[
                                                         z_max-z_min_calc] + gradient * (_z - z_max)

            self.average_gradient /= total_z_range
            self.T_borehole_calculated = np.zeros(self.z.size)
            self.T_borehole_calculated[-1] = T_bottom  # Anfangswert
            q_up = np.flip(np.cumsum(np.flip(q_in, axis=0)), axis=0)  # Massenflussrate [kg/s]
            q_up += 1e-6

            alpha = (q_in+ conductance_thermal) * dz / q_up

            for i in range(len(self.z) - 1, 0, -1):
                self.T_borehole_calculated[i - 1] = (self.T_borehole_calculated[i] + alpha[
                    i - 1] * dz * self.T_geothermal[i - 1]) / (
                            1 + alpha[i - 1])  # implizit

            self.bottom_point = '{} {}'.format(T[-1], self.z[-1])

        except:
            self.z, self.T_geothermal, self.T_borehole_calculated = [], [], []
            self.bottom_point = ''
            self.average_gradient = pd.NA

