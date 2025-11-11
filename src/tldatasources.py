from bokeh.models import ColumnDataSource
import tlconfiguration
from tldem import DEM
from tllogger import logger

import numpy as np
import pandas as pd

class DataSources:
    fields = None

    def __init__(self, log_data, infos_unique, result):

        self.log_data = log_data
        self.infos_unique = infos_unique
        self.result = result

        self.profile_list = [ColumnDataSource(data=dict(depth=[], value=[])) for _ in range(
            tlconfiguration.max_nr_logs)]

        # map
        self.map_boreholes = ColumnDataSource(data=dict(bh_id=infos_unique['borehole_id'].to_numpy(),
                                                      x=infos_unique['utm_easting'].to_numpy(),
                                                      y=infos_unique['utm_northing'].to_numpy()
                                                      )
                                            )
        logger.debug('Data source init: ' + str(infos_unique['borehole_id'].to_numpy().size) + ' boreholes')

        self.map_borehole_selected = ColumnDataSource(data=dict(bh_id=[], x=[], y=[]))  # selected point

        self.map_boreholes_quality = dict()
        for quality in tlconfiguration.log_qualities: # for map
            self.map_boreholes_quality[quality] = ColumnDataSource(data=dict(bh_id=[], x=[], y=[]))
        self.map_boreholes_drillingInduced = ColumnDataSource(data=dict(bh_id=[], x=[], y=[]))
        self.update_map_boreholes_for_quality()

        dem = DEM(infos_unique)

        no_dem = np.zeros((10, 10))
        image_data = np.where(no_dem == 0, np.nan, no_dem)

        self.map_background = ColumnDataSource(data={ 'image':[image_data ],#  [np.flipud(dem.matrix)],
                                                      'x': [dem.extent[0]], 'y': [dem.extent[2]],
                                                      'dw': [dem.extent[1] - dem.extent[0]],
                                                      'dh': [dem.extent[3] - dem.extent[2]] })

        # logs
        self.log_water_tables = ColumnDataSource(data=dict(z=[], T=[]))
        self.log_surface_temperature = ColumnDataSource(data=dict(z=[], T_landsat=[], T_modis=[]))

        self.log_points_selected = ColumnDataSource(data=dict(z=[], T=[]))

        self.T_geothermal = ColumnDataSource(data=dict(z=[], T=[]))
        self.T_borehole_calculated = ColumnDataSource(data=dict(z=[], T=[]))

        self.fit_range = ColumnDataSource(data=dict(T=[[],[]], z=[[],[]]))
        self.fit_line = ColumnDataSource(data=dict(T=[[],[]], z=[[],[]]))

    def set_fields(self, fields):
        self. fields = fields

    def update_for_borehole(self):
        borehole_id, sample_list = self.result.update.status.borehole_id, self.result.update.status.sample_list

        x_bh_selected, y_bh_selected = self.infos_unique.loc[
            self.infos_unique['borehole_id'] == borehole_id, 'utm_easting'].values[0], self.infos_unique.loc[
            self.infos_unique['borehole_id'] == borehole_id, 'utm_northing'].values[0]
        logger.debug('Data source update - selected borehole on map ' + str(borehole_id) + ': ' + str(
            x_bh_selected) + ', ' + str(y_bh_selected))
        self.map_borehole_selected.data = {'bh_id': [borehole_id], 'x': [x_bh_selected], 'y': [y_bh_selected]}

        # logs
        self.update_profile_list(borehole_id, sample_list)


        T_surface_landsat = self.log_data.infos.loc[self.log_data.infos['borehole_id'] == borehole_id,'T_surface_landsat'].values[0]
        T_surface_modis = self.log_data.infos.loc[self.log_data.infos['borehole_id'] == borehole_id, 'T_surface_modis'].values[0]
        logger.debug('Data source update - surface temperatures: ' + str(T_surface_modis)  + ' (modis) ' +
                     str(T_surface_landsat) + ' (landsat)')
        self.log_surface_temperature.data = {'z': [0.], 'T_landsat': [T_surface_landsat], 'T_modis': [T_surface_modis]  }

        self.update_water_tables(borehole_id, sample_list)

        self.update_points()
        self.update_fit()
        self.update_calculation()


    def update_map_boreholes_for_quality(self):
        merged_df = pd.merge(
            self.infos_unique[['utm_easting', 'utm_northing', 'borehole_id']],
            self.result.borehole_evaluation[['borehole_id', 'quality', 'drillingInduced']],
            on='borehole_id',
            how='inner'  # Inner Join
        )

        for quality in tlconfiguration.log_qualities:
            df = merged_df[merged_df['quality'] == quality]
            self.map_boreholes_quality[quality].data = {'bh_id': df['borehole_id'].to_numpy(),
                                                        'x': df['utm_easting'].to_numpy(),
                                                        'y': df['utm_northing'].to_numpy()   }

            logger.debug('Data source updata for quality ' + str(quality) + ': '  + str(df['borehole_id'].to_numpy().size) + ' boreholes')
            #print(quality, ' ', df['borehole_id'].to_numpy())

        df = merged_df[merged_df['drillingInduced'] == True]
        self.map_boreholes_drillingInduced.data = {'bh_id': df['borehole_id'].to_numpy(),
                                                    'x': df['utm_easting'].to_numpy(),
                                                    'y': df['utm_northing'].to_numpy()}
        logger.debug('Data source update for drilling-induced: ' + str(
            df['borehole_id'].to_numpy().size) + ' boreholes')

    def update_profile_list(self, borehole_id, sample_list):
        logger.debug('Data source update - profiles for samples: ' + str(sample_list))
        for ndx in range(len(sample_list)):
            profile = self.log_data.profiles[borehole_id + '_' + str(sample_list[ndx])]  # + str(sample)] # profiles[bh_id]  # Profil-Daten abrufen
            # Datenquelle für Profil aktualisieren
            if profile.z.size > 1:
                self.profile_list[ndx].data = {'depth': profile.z, 'value': profile['T']}
            else: # add point to have line if there is only one point
                self.profile_list[ndx].data = {'depth': [profile.z[0] - .5, profile.z[0] + .5] ,
                                               'value': [profile['T'][0], profile['T'][0]] }
        for ndx in range(len(sample_list), tlconfiguration.max_nr_logs):
            self.profile_list[ndx].data = {'depth':[], 'value':[]}


    def update_water_tables(self, borehole_id, sample_list):
        water_tables, T_water_tables = [0.] * len(sample_list), [0.] * len(sample_list)

        for ndx, sample_id in enumerate(sample_list):
            profile = self.log_data.profiles[borehole_id + '_' + sample_id]

            try:
                water_tables[ndx] = float(self.result.sample_evaluation.loc[
                                        (self.result.sample_evaluation['borehole_id'] == borehole_id) & (
                                                self.result.sample_evaluation[
                                                    'sample_id'].astype(str) == sample_id), 'water_table'].values[0])
                T_water_tables[ndx] = np.interp(water_tables[ndx], profile.z, profile['T'])
            except:
                pass

        logger.debug('Data source update - water tables: ' + str(water_tables))
        self.log_water_tables.data = {'z': water_tables,
                                                   'T': T_water_tables
                                                   }

    def update_water_table_for_borehole_sample(self, ndx):

        water_table = float(self.result.sample_evaluation.loc[
                                      (self.result.sample_evaluation['borehole_id'] ==
                                       self.result.update.status.borehole_id) & (
                                              self.result.sample_evaluation[
                                                  'sample_id'].astype(str) ==
                                              self.result.update.status.sample_list[ndx]), 'water_table'].values[0])
        print(str(ndx) + ' ' + str(water_table))
        profile = self.log_data.profiles[self.result.update.status.borehole_id + '_' +
                                         str(self.result.update.status.sample_list[ndx])]
        T_water_table = np.interp(water_table, profile.z, profile['T'])
        data = self.log_water_tables.data
        data['z'][ndx] = water_table # raises exception in take_data_from_info_spreadsheet(self), since data source empty
        data['T'][ndx] = T_water_table

        self.log_water_tables.data = dict(data)
        logger.debug('Data source update for sample ' +
                     str(self.result.update.status.sample_list[ndx])  +  ': Water table: ' + str(water_table) + ' ' + str(T_water_table))

    def update_points(self):
        logger.debug('Data source update: ' + str(self.result.points.number_of_points) + ' points')
        if self.result.points.number_of_points == 0:
            self.log_points_selected.data = {'z': [], 'T': []}
        else:
            self.log_points_selected.data = {
                'z': self.result.points.point_array[:self.result.points.number_of_points, 0].tolist(),
                'T': self.result.points.point_array[:self.result.points.number_of_points, 1].tolist()}

    def update_fit(self): # uses slider (it mus be up to date)
        logger.debug('Data source update - Fit line and range')
        if (self.fields.control_field.fit_checkbox.active and self.result.update.status.borehole_id != '' and
                self.result.update.status.selected_sample != tlconfiguration.selected_sample_initial):  # active

            profile_name = str(self.result.update.status.borehole_id) + '_' + str(
                self.result.update.status.selected_sample)

            if "." in profile_name:
                profile_name = profile_name.split(".")[0]

            T_min = self.log_data.profiles[profile_name]['T'].min()
            T_max = self.log_data.profiles[profile_name]['T'].max()

            value_stored = self.result.fitting.loc[self.result.fitting[
                                        'borehole_id'] == self.result.update.status.borehole_id, 'fit_m'].values[0]
            if pd.isna(value_stored):  # no stored fit results
                self.fit_range.data = {'T': [[T_min - 1, T_max + 1], [T_min - 1, T_max + 1]],
                                                    'z': [[self.fields.control_field.fit_slider.value[0],
                                                            self.fields.control_field.fit_slider.value[0]], # min
                                                           [self.fields.control_field.fit_slider.value[1],
                                                            self.fields.control_field.fit_slider.value[1]]]} # max
                self.fit_line.data = {'T': [], 'z': []}
            else: # take alreafy used and stored fit range
                fit_depth_top = self.result.fit.depth_range[0]
                fit_depth_bottom = self.result.fit.depth_range[1]

                self.fit_range.data = {'T': [[T_min - 1, T_max + 1], [T_min - 1, T_max + 1]],
                                                    'z': [[fit_depth_top, fit_depth_top],
                                                           [fit_depth_bottom, fit_depth_bottom]]}

                self.fit_line.data['T'] = [self.result.fit.T_depth_range]
                self.fit_line.data['z'] = [self.result.fit.get_depth_range()]
        else:  # not active
            self.fit_range.data = {'T': [[]], 'z': [[]]}
            self.fit_line.data = {'T': [], 'z': []}


    def update_calculation(self):
        logger.debug('Data source update - Calculation')

        value_stored = self.result.fitting.loc[
            self.result.fitting['borehole_id'] == self.result.update.status.borehole_id, 'calc_gradient'].values[0]

        if (self.fields.control_field.calculation_checkbox.active and not pd.isna(value_stored)
                and self.result.update.status.borehole_id != '' and
                self.result.update.status.selected_sample != tlconfiguration.selected_sample_initial):  # active

            z = self.result.calculation.z
            T_geothermal = self.result.calculation.T_geothermal
            T_borehole_calculated =  self.result.calculation.T_borehole_calculated
        else:
            z, T_geothermal, T_borehole_calculated = [],[], []

        self.T_geothermal.data = {'z': z, 'T': T_geothermal}
        self.T_borehole_calculated.data = {'z': z, 'T': T_borehole_calculated}