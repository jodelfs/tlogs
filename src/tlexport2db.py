import tlproject
from tllogger import logger
from tlpostprocessing import TemperatureCalculation

from sqlalchemy import create_engine #, MetaData
import pandas as pd
from geoalchemy2 import Geometry

class Export2DB:
    def __init__(self, log_data, result):
        user = 'postgres'
        password = 'postgres'

        schema = tlproject.db_schema  # Datenbankname, Datenbank muß bereits existieren,  z.B. über pgAdmin
        host = '127.0.0.1'  # localhost
        connection_string = 'postgresql://{}:{}@{}:5432/{}'.format(user, password, host, schema)
        self.engine = create_engine(connection_string)

        self.log_data = log_data
        self.infos_unique = log_data.infos.drop_duplicates(subset="borehole_id", keep="first")
        self.result = result

        self.export_result_frames = {#'log_infos': self.log_data.infos,
                              'borehole_evaluation': self.result.borehole_evaluation,
                              'fitting': self.result.fitting}

        self.postprocessing = TemperatureCalculation(log_data, result)

    def test_connection(self):
        try:
            with self.engine.connect() as connection:
                logger.info("Connection succeeded!")
        except Exception as e:
            logger.error("Failed connecting: {e}")

    def execute(self):
        self.result.update_borehole_evaluation_for_db_export()

        logger.info("Export to DB")
        self.test_connection()

        self.export_frame('log_infos', self.log_data.infos)
        for framename in self.export_result_frames:
            self.export_result_frame(framename)

        for temperture_calculation_method in [0, 1, 2]:
            self.export_temperatures(temperture_calculation_method=temperture_calculation_method)

    def export_result_frame(self, framename):
        if 'geometry' in self.export_result_frames[framename].columns.tolist():
            frame_merged = self.export_result_frames[framename]
            columns = self.export_result_frames[framename].columns.tolist()
        else:
            frame_merged= pd.merge(self.export_result_frames[framename],
                               self.infos_unique[['borehole_id', 'geometry']], on='borehole_id', how='inner')

            columns = self.export_result_frames[framename].columns.tolist() + ['geometry']
        #print(columns)
        frame_geom = frame_merged[columns]
        frame_geom_unique = frame_geom.drop_duplicates()
        self.export_frame(framename, frame_geom_unique)

    def export_frame(self, framename, frame):
        try:
            frame.to_sql(framename, self.engine, if_exists='replace', index=False,
                                                   dtype={'geometry': Geometry('POINT', srid=4326)})
            logger.info("\tDB export succeeded: " + framename)
        except Exception as e:
            logger.error(f"Error when exporting {framename}: {e}")

    def export_temperatures(self, temperture_calculation_method):
        _temperatures =self.infos_unique[['borehole_id',
                                   'geometry',
                                   #'sample_id',
                                   'T_surface_landsat',
                                    'T_surface_modis'
                                   ]]
        temperatures = _temperatures.drop_duplicates(subset='borehole_id', keep='first')

        #temperatures = pd.merge(temperatures, self.result.borehole_evaluation[['borehole_id', 'selected_sample']],
        #                         on='borehole_id', how='inner')
        #temperatures = temperatures[temperatures['selected_sample'] == temperatures['sample_id']]
        #temperatures.drop('selected_sample', axis=1, inplace=True)
        #temperatures.drop('sample_id', axis=1, inplace=True)

        temperatures = temperatures.merge(self.postprocessing.execute(temperture_calculation_method), on='borehole_id')

        try:
            if temperture_calculation_method == 0:
                table_name = 'temperatures'
            elif temperture_calculation_method == 1:
                table_name = 'temperatures_withsurfacetemperature'
            elif temperture_calculation_method == 2:
                table_name = 'temperatures_approximation'
            else:
                logger.error(f"Error temperature calculation method not supported")
                table_name = 'dummytable'


            temperatures.to_sql(table_name, self.engine, if_exists='replace', index=False,
                                   dtype={'geometry': Geometry('POINT', srid=4326)})
            logger.info("\tDB export succeeded: {}".format(table_name))
        except Exception as e:
            logger.error(f"Error when exporting temperatures: {e}")