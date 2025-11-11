from tllogger import logger
import tlconfiguration

class NoteCallbacks:

    def __init__(self, data_sources, result, fields):
        self.data_sources = data_sources
        self.result = result
        self.fields = fields

    def note_evaluation_changed(self, attr, old, new):
        if self.result.update.status.borehole_id != ''  and not self.result.update.status.borehole_changing:
            self.result.update.update_borehole_evaluation('note_evaluation', new)

    def note_borehole_changed(self, attr, old, new):
        if self.result.update.status.borehole_id != '' and not self.result.update.status.borehole_changing:
            #logger.debug('Borehole note changed: ' + str(new)[:20])
            self.fields.note_field.note_borehole_changed(new)

    def note_sample_changed(self, attr, old, new, ndx):
        if self.result.update.status.borehole_id != ''and not self.result.update.status.borehole_changing:
            logger.debug('Field note for sample ' + str(
                self.result.update.status.sample_list[
                    ndx]) + ' changed: ' + str(new)[:tlconfiguration.debug_note_length].replace('\n', ' '))
            self.fields.note_field.update_note_sample(new, ndx)

            self.data_sources.update_water_table_for_borehole_sample(ndx)
            self.fields.log_field.log_plot.update_sample_properties(ndx)