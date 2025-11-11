from tllogger import logger
import tlconfiguration

class Status:
    def __init__(self):
        self.__borehole_id = ''
        self.__sample_list = None
        self.__selected_sample = tlconfiguration.selected_sample_initial
        self.__borehole_changing = False

    @property
    def borehole_id(self):
        return self.__borehole_id

    @property
    def sample_list(self):
        return self.__sample_list

    @property
    def selected_sample(self):
        return self.__selected_sample

    @property
    def borehole_changing(self):
        return self.__borehole_changing

    @borehole_id.setter
    def borehole_id(self, id):
        self.__borehole_id = id
        logger.info('Status update - Selected borehole: ' + str(id))

    @sample_list.setter
    def sample_list(self, _list):
        self.__sample_list = _list
        logger.debug('Status update - Sample list: ' + str(_list))

        if len(_list) > tlconfiguration.max_nr_logs:
            logger.error("Not enough DataSources for logs")

    @selected_sample.setter
    def selected_sample(self, value):
        self.__selected_sample = value
        logger.debug('Status update - Selected sample: ' + str(value))

    @borehole_changing.setter
    def borehole_changing(self, value):
        self.__borehole_changing = value