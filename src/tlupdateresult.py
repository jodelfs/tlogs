import tlconfiguration
from tllogger import logger
from tlstatus import Status

class UpdateResult:
    def __init__(self, result):
        self.result = result
        self.status = Status()

    def update_fitting(self, column, value):
        if self.status.borehole_id != '':
            logger.debug('Result fitting column ' + column + ' changed: ' + str(value)[:tlconfiguration.debug_note_length].replace('\n', ' '))
            self.result.fitting.loc[
                self.result.fitting['borehole_id'] == self.status.borehole_id, column] = value

    def update_borehole_evaluation(self, column, value):
        if self.status.borehole_id != '':
            logger.debug('Result borehole evaluation column ' + column + ' changed: ' + str(value)[:tlconfiguration.debug_note_length].replace('\n', ' '))
            self.result.borehole_evaluation.loc[
                self.result.borehole_evaluation['borehole_id'] == self.status.borehole_id, column] = value

    def update_sample_evaluation(self, sample_id, column, value):
        if self.status.borehole_id != '' and sample_id != tlconfiguration.selected_sample_initial:
            logger.debug('Result sample evaluation ' + column + ' changed for sample ' + str(
                sample_id) + ': ' + str(value)[:tlconfiguration.debug_note_length].replace('\n', ' '))

            self.result.sample_evaluation.loc[
                (self.result.sample_evaluation['borehole_id'] == self.status.borehole_id) & (
                        self.result.sample_evaluation['sample_id'].astype(str) == str(sample_id)), column] = value
