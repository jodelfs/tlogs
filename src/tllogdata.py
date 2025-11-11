import pandas as pd
from os import listdir
from os.path import isfile, join
import re

from tlreports import Reports
from tllogger import logger

class LogData:
    profiles = None # dict of dataFramers
    infos = None # dataFrame
    boreholes = None # list of strings for boreholes
    samples_at_borehole = None # dict
    path_pdfs = None
    reports = None

    def set_path_pdfs(self, path_pdfs):
        self.path_pdfs = path_pdfs

    def set_profiles(self, filepath):
        print("Set profiles")
        # serch for csv files in directory
        # sets dict of dataframees for profiles
        csvfilenames = [f for f in listdir(filepath) if isfile(join(filepath, f))]
        self.profilenames = [name[: -4] for name in csvfilenames]  # remove ending .csv

        self.profiles = dict()
        for profilename in self.profilenames:
            #print(profilename)
            try:
                first_row = pd.read_csv('{}/{}.csv'.format(filepath, profilename),
                                        nrows=1, sep=r'[,\t]', engine='python', header=None)
                # Prüfen, ob die erste Zeile Buchstaben enthält
                has_header = bool(re.search(r'[a-zA-Z]', first_row.iloc[0].to_string()  )) # first_row.astype(str).apply(lambda x: x.str.match(r'[A-Za-z]').any()).any()
                # Datei erneut einlesen mit der ermittelten Header-Option
                self.profiles[profilename] = pd.read_csv('{}/{}.csv'.format(filepath, profilename),
                                                         sep=r'[,\t]',
                                                         engine='python',
                                                         header=0 if has_header else None,
                                                         usecols=[0, 1], names=['z', 'T']
                                                         )
            except:
                logger.warning("Failed reading profile " + str(profilename))
        #print(self.profiles['6422_00020_a'])

    def set_infos(self, borehole_infos_file):
        print("Set infos")
        #try:
        logger.info('Read info file:\n\t' + borehole_infos_file)
        self.infos = pd.read_csv(borehole_infos_file, header=0)#, index_col=0)# encoding="ISO-8859-1", low_memory=False) # , nrows = 20)
        #except UnicodeDecodeError:
        #    self.infos = pd.read_csv(borehole_infos_file, header=0, index_col=0,  encoding="ISO-8859-1")  # , nrows = 20)

        # boreholes are identified by a new column 'borehole_id'. The location id (LOCID) seems not suitable
        # since there are rows with different coordinates (UTM_OST, UTM_NORD ) for the same location id in the spreadsheet
        # the project id (PRJ_ID) varies in these cases -> identify boreholes by combining both ids
        #self.infos['borehole_id'] = self.infos['PRJ_ID'] + '_' + self.infos['LOCID'].astype(str)  # identifier for borehole

        self.boreholes = list(self.infos['borehole_id'].unique()) # = list of boreholes

        # self.boreholes = list(map(str, self.infos['borehole_id'].unique()))
        ### !!!! überprüfeb, wenn samples in spreadsheet
        self.samples_at_borehole = dict()  # to loop over samples for a borehole
        for borehole in self.boreholes:
            self.samples_at_borehole[borehole] = sorted([sample.rsplit("_", 1)[-1]
                                                 for sample in self.profilenames if '_'.join(sample.split("_")[:-1]) == borehole])   #.startswith(borehole)])

        #for sample in self.profilenames:
        #    print('_'.join(sample.split("_")[:-1]))
        self.reports = Reports(self.infos)

    def update_infos(self, borehole_id, sample_id, column, value):
        logger.info('\tinfos column {} changed for borehole_id {}, sample_id {}: {}'.format( column, borehole_id, sample_id, value))

        self.infos.loc[
            (self.infos['borehole_id'] == borehole_id) & (
                    self.infos['sample_id'].astype(str) == str(sample_id)), column] = value
