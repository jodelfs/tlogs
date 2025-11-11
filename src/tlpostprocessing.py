import tlconfiguration
from tllogger import logger

import pandas as pd
import numpy as np

class PostProcessing:
    def execute(self):
        pass

class TemperatureCalculation(PostProcessing):
    def __init__(self, log_data, result):
        self.log_data = log_data
        self.result = result

    def execute(self, temperture_calculation_method):
        df_temp = pd.DataFrame({'borehole_id': self.log_data.boreholes})

        for depth in tlconfiguration.depth_list:
            df_temp['T_{}'.format(depth)] = np.nan * len(self.log_data.boreholes)  # column for result

        try:
            for borehole_id in self.log_data.boreholes:
                if temperture_calculation_method < 2: # not approximation
                    if str(self.result.borehole_evaluation.loc[
                               self.result.borehole_evaluation['borehole_id'] == borehole_id, 'selected_sample'].values[
                               0]) != '0':
                        number_of_subsurfacePoints, points_subsurface = self.result.points.get_points(borehole_id)
                        if number_of_subsurfacePoints > 0:
                            if temperture_calculation_method == 0: # no surface temperatue from satellite
                                points_all = points_subsurface

                                points_all_sorted = points_all[points_all[:, 0].argsort()]
                                depth_arr = points_all_sorted[:, 0]
                                T_arr = points_all_sorted[:, 1]

                                depth_top = min(depth_arr[depth_arr > 0])
                                # depth_top = df_borehole_evaluation.loc[df_borehole_evaluation['borehole_id'] == borehole, 'depth_low'].values[0] if subsurface_only else
                                # depth_top = min(depth_arr[depth_arr > 0])  # if subsurface_only else 0.

                            else: # with surface temperature from satellite

                                T_surface = self.log_data.infos.loc[
                                    self.log_data.infos['borehole_id'] == borehole_id, 'T_surface_landsat'].values[0]
                                #point_surface = np.array([0, T_surface]).reshape(1, 2)

                                points_all = points_subsurface

                                points_all_sorted = points_all[points_all[:, 0].argsort()]
                                depth_arr = np.array([0., points_all_sorted[-1, 0]])
                                T_arr = np.array([T_surface, points_all_sorted[-1, 1]])

                                depth_top = 0

                            for depth in tlconfiguration.depth_list:
                                T_depth = np.nan if depth < depth_top or depth > max(depth_arr) else float(
                                    np.interp(depth, depth_arr, T_arr))
                                df_temp.loc[df_temp['borehole_id'] == borehole_id, 'T_{}'.format(depth)] = T_depth

                elif temperture_calculation_method == 2:  # approximation
                    T_surface = self.log_data.infos.loc[
                        self.log_data.infos['borehole_id'] == borehole_id, 'T_surface_landsat'].values[0]

                    selected_sample = str(int(self.result.borehole_evaluation.loc[
                        self.result.borehole_evaluation['borehole_id'] == borehole_id, 'selected_sample'].values[0]))
                    if selected_sample != tlconfiguration.selected_sample_initial:
                        z = self.log_data.profiles[
                            borehole_id + '_' + selected_sample].tail(1)[
                            'z'].iloc[0] # lowest point
                        T = self.log_data.profiles[
                            borehole_id + '_' + selected_sample].tail(1)[
                            'T'].iloc[0]  # BHT
                    else: # for BW
                        z = self.log_data.profiles[borehole_id + '_a'].tail(1)['z'].iloc[0] # lowest point
                        T = self.log_data.profiles[borehole_id + '_a'].tail(1)['T'].iloc[0]  # BHT

                    depth_arr = np.array([0., z])
                    T_arr = np.array([T_surface, T])
                    #print(depth_arr, ' ', T_arr)
                    depth_top = 0.

                    for depth in tlconfiguration.depth_list:
                        T_depth = np.nan if depth < depth_top or depth > max(depth_arr) else float(
                            np.interp(depth, depth_arr, T_arr))
                        df_temp.loc[df_temp['borehole_id'] == borehole_id, 'T_{}'.format(depth)] = T_depth
                else:
                    logger.error(
                        f"Error temperature calculation method {temperture_calculation_method} not supported")
        except:
            logger.warning(f"Temperature calculation failed for {borehole_id}")

        return df_temp