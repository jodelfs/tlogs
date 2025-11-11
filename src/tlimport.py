from tllogdata import LogData
from tlresult import Result
import tlproject

class Import:

    def read_data(self):
        log_data, infos_unique = self.read_log_data()
        result = self.read_evaluation_data(log_data)

        # print(result.fitting)
        result.preprocess()

        return log_data, infos_unique, result

    def read_log_data(self):
        print("Read log data")
        log_data = LogData()
        log_data.set_profiles(tlproject.path_input)
        log_data.set_infos(tlproject.file_name_borehole_infos)
        log_data.set_path_pdfs(tlproject.path_pdfs)

        infos_unique = log_data.infos.drop_duplicates(subset="borehole_id", keep="first")

        return log_data, infos_unique

    def read_evaluation_data(self, log_data):
        result = Result(log_data)
        result.load_from_file()

        return result

