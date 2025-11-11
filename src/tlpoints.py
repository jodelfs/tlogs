import tlconfiguration
from tllogger import logger

import numpy as np

class Points:
    #borehole_id = None
    number_of_points = 0
    point_array = None  # [[dept_0, T_0], ...]

    attach_to_sample = None
    log_plot = None

    def __init__(self, result, log_data):
        self.fitting = result.fitting

    def set_fields(self, fields):
        self.attach_to_sample = fields.control_field.attach_to_sample
        self.log_plot = fields.log_field.log_plot

    def get_depth_range(self):
        depth_top = float(np.min(self.point_array[:self.number_of_points, 0])) \
            if self.number_of_points > 0 else tlconfiguration.depth_top_initial
        depth_bottom = float(np.max(self.point_array[:self.number_of_points, 0])) \
            if self.number_of_points > 0 else tlconfiguration.depth_bottom_initial
        return depth_top, depth_bottom

    def update_for_borehole(self, borehole_id):
        #self.borehole_id = borehole_id

        self.number_of_points, self.point_array = self.get_points(borehole_id)
        logger.debug('Points update: ' + str(self.number_of_points) + ' points')

    def get_points(self, borehole_id):
        number_of_points = int(
            self.fitting.loc[self.fitting['borehole_id'] == borehole_id, 'number_of_points'].values[0])

        ndx = self.fitting.loc[self.fitting[
                                   'borehole_id'] == borehole_id].index[0]

        numpy_arraystring_cleaned = self.fitting.at[ndx, 'points'].replace('\n', '').replace('[',
                                                                                             '').replace(
            ']', '').strip()
        points = np.fromstring(numpy_arraystring_cleaned, sep=' ').reshape(tlconfiguration.max_nr_pnts, 2)

        return number_of_points, points

    def get_result(self):
        return self.number_of_points, np.array2string(self.point_array)

    def add(self, profile, event):
        if self.number_of_points >= tlconfiguration.max_nr_pnts:
            logger.error("Cannot add another point, there are already " + str(tlconfiguration.max_nr_pnts))
        else:  # if number_of_points > 0:
            selected_z = round(event.y, 1)

            if self.attach_to_sample.active:
                if selected_z < np.min(profile.z):
                    selected_z = np.min(profile.z)
                if selected_z > np.max(profile.z):
                    selected_z = np.max(profile.z)

                self.point_array[self.number_of_points, 1] = np.round(
                    np.interp(np.ones(1) * selected_z, profile.z, profile['T']),2)
            else:
                self.point_array[self.number_of_points, 1] = round(event.x, 2)

            self.point_array[self.number_of_points, 0] = selected_z

            self.number_of_points += 1

            logger.debug('New point: ' + str(
                self.point_array[self.number_of_points-1, 0]) + ' ' + str(
                self.point_array[self.number_of_points-1, 1]))

            self.log_plot.last_point_label.x = self.point_array[self.number_of_points - 1, 1]
            self.log_plot.last_point_label.y = selected_z
            self.log_plot.last_point_label.text = f"({self.point_array[self.number_of_points - 1, 1]:.2f}, {selected_z:.2f})"

    def delete(self):
        if self.number_of_points > 0:
            self.number_of_points -= 1
            logger.debug('Delete point: ' + str(self.point_array[self.number_of_points , 0]) + ' ' + str(
                self.point_array[self.number_of_points, 1]))

            self.point_array[self.number_of_points, 0] = 0.
            self.point_array[self.number_of_points, 1] = 0.

            self.log_plot.last_point_label.text = ''

    def delete_all(self):
        if self.number_of_points > 0:
            logger.debug('Deleta all points')
            self.number_of_points = 0
            self.point_array = np.zeros(2 * tlconfiguration.max_nr_pnts).reshape(tlconfiguration.max_nr_pnts, 2)

            self.log_plot.last_point_label.text = ''
