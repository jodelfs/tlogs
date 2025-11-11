
import tlproject
import tlconfiguration
from tlupdateresult import UpdateResult
from tllogger import logger

from tlpoints import Points
from tlfit import Fit
from tlcalculation import Calculation
import tlproject

import pandas as pd
import numpy as np
from math import sqrt

def generate_zeros(n):
    return "[ " + "\n ".join(["[0. 0.]"] * n) + " ]"

class Result:
    points_initial = generate_zeros(tlconfiguration.max_nr_pnts)

    def __init__(self, log_data):

        self.log_data = log_data

        self.update = UpdateResult(self)

        boreholes = log_data.boreholes

        self.fitting = pd.DataFrame({
            'borehole_id' : boreholes,
            'number_of_points': [0] * len(boreholes),
            'points': [self.points_initial]  * len(boreholes),
            'depth_top': [tlconfiguration.depth_top_initial] * len(boreholes),
            'depth_bottom': [tlconfiguration.depth_bottom_initial] * len(boreholes),
            'fit_m': [pd.NA] * len(boreholes),
            'fit_c': [pd.NA] * len(boreholes),
            'fit_std_m': [pd.NA] * len(boreholes),
            'fit_std_c': [pd.NA] * len(boreholes),
            'fit_depth_top':[pd.NA] * len(boreholes),
            'fit_depth_bottom': [pd.NA] * len(boreholes),
            'calc_bottom_point' : ['0. 0.'] * len(boreholes),
            'calc_gradient': [''] * len(boreholes),
            'selected_method': [0] * len(boreholes) # points as default
        })

        self.points = Points(self, log_data)
        self.fit = Fit(self, log_data)
        self.calculation = Calculation(self, log_data)

        # borehole_evaluation
        self.borehole_evaluation = pd.DataFrame({
            'borehole_id' : boreholes,
            'selected_sample':  [tlconfiguration.selected_sample_initial] * len(boreholes),
            'deactivated' : [False] * len(boreholes),
            'quality': [tlconfiguration.quality_initial] * len(boreholes),
            'drillingInduced': [False] * len(boreholes),
            'note_evaluation': [tlconfiguration.note_initial] * len(boreholes),
            #'note_borehole': [tlconfiguration.note_initial] * len(boreholes),
            'static_water_level': [tlconfiguration.static_water_level_initial] * len(boreholes),
            'date': [tlconfiguration.date_initial] * len(boreholes),
            'elevation': [tlconfiguration.elevation_initial] * len(boreholes),
            #'sealing': [tlconfiguration.sealing_initial] * len(boreholes),
            #'vegetation': [tlconfiguration.vegetation_initial] * len(boreholes),
            #'land_use': [tlconfiguration.land_use_initial] * len(boreholes),
            #'land_cover': [tlconfiguration.land_cover_initial] * len(boreholes),
            #'tree_cover': [tlconfiguration.tree_cover_initial] * len(boreholes),
            'flow_info': [1] * len(boreholes), # 0: No info, 1: production / injection eate knows, 2: inflow zones determined, 3: inflow rrates determined, 4: flow during shut-in determined
            'time_info': [1] * len(boreholes),  # 0: No info, 1: day known, 2: duration known, 3: clear sequence
            'borehole_info': [1] * len(boreholes),  # 0: No info, 1: type given, 2: measures given, 3: more details
            'lithology_info': [0] * len(boreholes),  # 0: No info, 1: some info, 2: lots of info
            'nr_samples': [pd.NA] * len(boreholes),
            'depth_top': [pd.NA] * len(boreholes),
            'depth_bottom': [pd.NA] * len(boreholes),
            #'slope': [tlconfiguration.slope_initial] * len(boreholes),
            #'aspect': [tlconfiguration.aspect_initial] * len(boreholes),
            #'N112': [tlconfiguration.Nxxx_initial] * len(boreholes),
            #'N120': [tlconfiguration.Nxxx_initial] * len(boreholes),
            #'N211': [tlconfiguration.Nxxx_initial] * len(boreholes),
            #'N311': [tlconfiguration.Nxxx_initial] * len(boreholes)
        })

        self.borehole_evaluation = self.borehole_evaluation.merge(
            log_data.infos.drop_duplicates(subset="borehole_id", keep="first")[['borehole_id', 'note_borehole']],
            on='borehole_id',
            how='left'  # oder 'inner', wenn du nur gemeinsame behalten willst
        )

        # sample_evaluation
        self.sample_evaluation = log_data.infos[['borehole_id',
                                                 'sample_id',
                                                 'global_sample_id',
                                                 'date',
                                                 'time',
                                                 'operation',
                                                 'water_table',
                                                 'note_sample'
                                                 ]]

        self.result_frames = {
            'fitting': self.fitting,
            'boreholeEvaluation': self.borehole_evaluation,
            'sampleEvaluation': self.sample_evaluation
        }

    def load_from_file(self):
        logger.info('Load result files')

        for result_type in self.result_frames:
            filename = tlproject.path_result + '/' + result_type + '_' + tlproject.result_file_identifier + '.csv'
            try:
                logger.info('\t' + result_type)
                result_from_file = pd.read_csv(filename, index_col=0)
                # borehole_evaluation_from_file.drop(columns=[f"note_measurement_{i}" for i in range(20)], inplace=True)
                index_label = 'global_sample_id' if result_type == 'sampleEvaluation' else 'borehole_id'

                #print("Columns in", filename, ":", result_from_file.columns.tolist())
                #print("First rows:\n", self.result_frames[result_type].head())
                self.result_frames[result_type].set_index(index_label, inplace=True)  # Gemeinsamen Schlüssel als Index setzen
                result_from_file.set_index(index_label, inplace=True)

                self.result_frames[result_type].update(result_from_file)
                #self.result_frames[result_type] = pd.merge(
                #    self.result_frames[result_type],
                #    result_from_file,
                #    on=index_label,
                #    how="inner",
                #    #suffixes=("", "_new")
                #)

                # Index zurücksetzen, falls nötig
                self.result_frames[result_type].reset_index(inplace=True)
            except:
                logger.warning('Failed loading ' + filename)

    def set_depth_range(self):
        logger.info('Preprocessing - Set result fitiing depth_top, depth_bottom (of points set)')
        for ndx in range(self.fitting.shape[0]):
            if self.points.number_of_points > 0:
                self.fitting.loc[ndx, 'depth_top'], self.fitting.loc[ndx, 'depth_bottom'] = (
                    float(np.min(self.points.point_array[:self.points.number_of_points, 0])), float(
                        np.max(self.points.point_array[:self.points.number_of_points, 0])))

    def set_date(self):
        logger.info('Preprocessing - Set result borehole date (from selected sample or no date)')
        for borehole_id in self.log_data.boreholes:
            try:
                selected_sample = self.borehole_evaluation.loc[self.borehole_evaluation['borehole_id'] == borehole_id , 'selected_sample']. values[0]
                if str(selected_sample) != tlconfiguration.selected_sample_initial:
                    date = self.log_data.infos.loc[(self.log_data.infos['borehole_id'] == borehole_id) & (
                            self.log_data.infos['sample_id'].astype(str) == str(selected_sample)), 'date'].values[0]
                    self.borehole_evaluation.loc[self.borehole_evaluation['borehole_id'] == borehole_id, 'date'] = date
            except:
                pass

    def set_borehole_evaluation_infos(self):
        logger.info('Preprocessing - Set result borehole nr_samples - depth_top, depth_bottom (of all samples)')
        sample_counts = self.log_data.infos.groupby('borehole_id')['sample_id'].nunique()
        self.borehole_evaluation['nr_samples'] = self.borehole_evaluation['borehole_id'].map(sample_counts)
        for borehole_id in self.log_data.boreholes:
            z_min, z_max = 10000., 0.
            for sample_id in self.log_data.samples_at_borehole[borehole_id]:
                profile = self.log_data.profiles[str(borehole_id) + '_' + str(sample_id)]
                if profile.z.min() < z_min:
                    z_min = profile.z.min()
                if profile.z.max() > z_max:
                    z_max = profile.z.max()

            self.borehole_evaluation.loc[self.borehole_evaluation['borehole_id'] == borehole_id, 'depth_top'] = float(z_min)
            self.borehole_evaluation.loc[self.borehole_evaluation['borehole_id'] == borehole_id, 'depth_bottom'] = float(z_max)

    def update_borehole_evaluation_for_db_export(self):
        # update date, static_water_table accoring to selected_sampe before writing in database

        self.sample_evaluation = self.sample_evaluation.drop_duplicates(
            subset=["borehole_id", "sample_id"],
            keep="first"  # behält die erste Zeile, löscht alle weiteren
        )

        map_dates = self.sample_evaluation.set_index(["borehole_id", "sample_id"])["date"]
        self.borehole_evaluation["date"] = self.borehole_evaluation.apply(
            lambda row: map_dates.get((row["borehole_id"], row["selected_sample"])),
            axis=1
        )

        map_water_tables = self.sample_evaluation.set_index(["borehole_id", "sample_id"])["water_table"]
        self.borehole_evaluation["static_water_table"] = self.borehole_evaluation.apply(
            lambda row: map_water_tables.get((row["borehole_id"], row["selected_sample"])),
            axis=1
        )


    def preprocess(self):
        logger.info('Preprocessing - Set result borehole static water level')
        for borehole_id in self.log_data.boreholes:
            self.borehole_evaluation.loc[self.borehole_evaluation[
                                             'borehole_id'] == borehole_id, 'static_water_level'] = self.calculate_static_water_level(borehole_id)

        logger.info('Preprocessing - Set result borehole elevation')
        for borehole_id in self.log_data.boreholes:
            elevation = self.log_data.infos.loc[self.log_data.infos['borehole_id'] == borehole_id, 'elevation'].values[
                0]
            self.borehole_evaluation.loc[
                self.borehole_evaluation['borehole_id'] == borehole_id, 'elevation'] = float(
                elevation)  # float to avoid numpy float in psql import

        if False: # TO BE REMOVED
            sealing = self.log_data.infos.loc[self.log_data.infos['borehole_id'] == borehole_id, 'sealing'].values[
                0]
            self.borehole_evaluation.loc[
                self.borehole_evaluation['borehole_id'] == borehole_id, 'sealing'] = float(
                sealing)  # float to avoid numpy float in psql import

            vegetation = self.log_data.infos.loc[self.log_data.infos['borehole_id'] == borehole_id, 'vegetation'].values[
                0]
            self.borehole_evaluation.loc[
                self.borehole_evaluation['borehole_id'] == borehole_id, 'vegetation'] = float(
                vegetation)  # float to avoid numpy float in psql import

            land_use = self.log_data.infos.loc[self.log_data.infos['borehole_id'] == borehole_id, 'land_use'].values[
                0]
            self.borehole_evaluation.loc[
                self.borehole_evaluation['borehole_id'] == borehole_id, 'land_use'] = land_use # float to avoid numpy float in psql import

            land_cover = self.log_data.infos.loc[self.log_data.infos['borehole_id'] == borehole_id, 'land_cover'].values[
                0]
            self.borehole_evaluation.loc[
                self.borehole_evaluation[
                    'borehole_id'] == borehole_id, 'land_cover'] = land_cover  # float to avoid numpy float in psql import

            tree_cover = self.log_data.infos.loc[self.log_data.infos['borehole_id'] == borehole_id, 'tree_cover'].values[
                0]
            self.borehole_evaluation.loc[
                self.borehole_evaluation[
                    'borehole_id'] == borehole_id, 'tree_cover'] = float(tree_cover)  # float to avoid numpy float in psql import

            slope = self.log_data.infos.loc[self.log_data.infos['borehole_id'] == borehole_id, 'slope'].values[
                0]
            self.borehole_evaluation.loc[
                self.borehole_evaluation[
                    'borehole_id'] == borehole_id, 'slope'] = float(slope)  # float to avoid numpy float in psql import

            aspect = self.log_data.infos.loc[self.log_data.infos['borehole_id'] == borehole_id, 'aspect'].values[
                0]
            self.borehole_evaluation.loc[
                self.borehole_evaluation[
                    'borehole_id'] == borehole_id, 'aspect'] = float(aspect)  # float to avoid numpy float in psql import

            # land use
            N112 = self.log_data.infos.loc[self.log_data.infos['borehole_id'] == borehole_id, 'N112'].values[
                0]
            self.borehole_evaluation.loc[
                self.borehole_evaluation[
                    'borehole_id'] == borehole_id, 'N112'] = float(N112)  # float to avoid numpy float in psql import

            N112 = self.log_data.infos.loc[self.log_data.infos['borehole_id'] == borehole_id, 'N112'].values[
                0]
            self.borehole_evaluation.loc[
                self.borehole_evaluation[
                    'borehole_id'] == borehole_id, 'N112'] = float(N112)  # float to avoid numpy float in psql import


            N112 = self.log_data.infos.loc[self.log_data.infos['borehole_id'] == borehole_id, 'N112'].values[
                0]
            self.borehole_evaluation.loc[
                self.borehole_evaluation[
                    'borehole_id'] == borehole_id, 'N112'] = float(N112)  # float to avoid numpy float in psql import


            N120 = self.log_data.infos.loc[self.log_data.infos['borehole_id'] == borehole_id, 'N120'].values[
                0]
            self.borehole_evaluation.loc[
                self.borehole_evaluation[
                    'borehole_id'] == borehole_id, 'N120'] = float(N120)  # float to avoid numpy float in psql import


            N211 = self.log_data.infos.loc[self.log_data.infos['borehole_id'] == borehole_id, 'N211'].values[
                0]
            self.borehole_evaluation.loc[
                self.borehole_evaluation[
                    'borehole_id'] == borehole_id, 'N211'] = float(N211)  # float to avoid numpy float in psql import

            N311 = self.log_data.infos.loc[self.log_data.infos['borehole_id'] == borehole_id, 'N311'].values[
                0]
            self.borehole_evaluation.loc[
                self.borehole_evaluation[
                    'borehole_id'] == borehole_id, 'N211'] = float(N311)  # float to avoid numpy float in psql import


        self.set_borehole_evaluation_infos() # nr samples, depths
        # consider previous evaluations
        self.set_depth_range()
        self.set_date()

    def update_for_borehole(self, borehole_id):
        self.update.borehole_id = borehole_id
        logger.debug('Set update result borehole id: ' + str(borehole_id))
        self.points.update_for_borehole(borehole_id)

    def get_field_value_for_borehole(self, field): # in order to update fields
        value = self.borehole_evaluation.loc[
            self.borehole_evaluation['borehole_id'] == self.update.status.borehole_id, field].values[0]
        logger.debug('Field update - ' + field + ': ' + str(value)[:tlconfiguration.debug_note_length])
        return value
    
    def calculate_static_water_level(self, borehole_id):
        static_water_level = 0.
        count = 0
        try:
            for sample_id in self.log_data.samples_at_borehole[borehole_id]:
                operation = self.sample_evaluation.loc[
                    (self.sample_evaluation['borehole_id'] == borehole_id) & (
                            self.sample_evaluation['sample_id'].astype(str) == str(
                        sample_id)), 'operation'].values[0]

                if str(operation).lower() == 'shut-in':
                    static_water_level_running = float(self.sample_evaluation.loc[
                                                           (self.sample_evaluation['borehole_id'] == borehole_id) & (
                                                                   self.sample_evaluation['sample_id'].astype(
                                                                       str) == str(
                                                               sample_id)), 'water_table'].values[0])
                    static_water_level += static_water_level_running
                    count += 1
        except:
            pass

        return static_water_level / count if count > 0 else pd.NA

    def update_points(self):
        number_of_points, points_string = self.points.get_result()
        self.update.update_fitting("points", points_string)
        self.update.update_fitting("number_of_points", number_of_points)
        self.update.update_fitting("depth_top", self.points.get_depth_range()[0])
        self.update.update_fitting("depth_bottom", self.points.get_depth_range()[1])

    def update_fit(self):
        param, param_cov = self.fit.get_result()
        depth_top, depth_bottom = self.fit.get_depth_range()

        # logger.debug('Update result fit: ' + str(param) + ' ' + str(param_cov) + ' ' + str(depth_top) + ' ' + str(depth_bottom))

        self.update.update_fitting("fit_m", float(param[0]))
        self.update.update_fitting("fit_c", float(param[1]))
        self.update.update_fitting("fit_std_m", float(sqrt(param_cov[0][0])))
        self.update.update_fitting("fit_std_c", float(sqrt(param_cov[1][1])))
        self.update.update_fitting("fit_depth_top", float(depth_top))
        self.update.update_fitting("fit_depth_bottom", float(depth_bottom))

    def update_calculation(self):

        bottom_point, average_gradient = self.calculation.get_result()

        self.update.update_fitting("calc_bottom_point", bottom_point)
        self.update.update_fitting("calc_gradient", average_gradient)
