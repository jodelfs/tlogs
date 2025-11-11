from tllogger import logger
import tlproject

class CSVExportItem:
    def __init__(self, frame, file):
        self.frame = frame
        self.file = file

class Export2CSV:
    def __init__(self, log_data, result):
        self.log_data = log_data
        self.result = result

        self.items = {}
        for result_type in self.result.result_frames:
            self.items[result_type] =CSVExportItem(self.result.result_frames[result_type], tlproject.path_result + '/' +
                                                   result_type + '_' + tlproject.result_file_identifier + '.csv')

        self.items['infos'] = CSVExportItem(self.log_data.infos, tlproject.file_name_borehole_infos)

    def execute(self):
        logger.info("Export into CSV-files for " + tlproject.result_file_identifier + ':')
        for name in self.items:
            try:
                self.items[name].frame.to_csv(self.items[name].file)#, index=False)
                logger.info('\tCSV export succeeded: ' + name)
            except:
                logger.error("Failed exporting CSV file " + name)

