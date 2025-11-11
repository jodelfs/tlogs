from tllogger import logger
import tlconfiguration

class SelectionCallbacks:
    def __init__(self, data_sources, log_data, infos_unique, result, fields):
        self.data_sources = data_sources
        self.log_data = log_data
        self.infos_unique = infos_unique

        self.result = result
        self.fields = fields

    def clicked_on_map(self, attr, old, new):
        logger.debug('Search new borehole on map: ' + str(new))
        if len(new) == 0:
            return
        elif self.data_sources.map_boreholes.data['bh_id'][new[0]] not in self.log_data.samples_at_borehole:
            return

        borehole_id = self.data_sources.map_boreholes.data['bh_id'][new[0]]
        self.fields.control_field.borehole.value = borehole_id

    def borehole_selection_field_changed(self, attr, old, new):
        logger.debug('Borehole selection field changed: ' + str(new))
        if new not in self.log_data.samples_at_borehole:
            return

        self.borehole_changed(new)

    def borehole_changed(self, borehole_id):
        self.result.update.status.borehole_changing = True

        self.result.update.status.borehole_id = borehole_id
        self.result.update.status.sample_list = sorted(self.log_data.samples_at_borehole[borehole_id])
        self.fields.update_for_borehole()

        self.result.points.update_for_borehole(borehole_id)
        self.result.fit.update_for_borehole(borehole_id)
        self.result.calculation.update_for_borehole(borehole_id)

        #self.result.update_calculation() # not needed for points, fit

        self.data_sources.update_for_borehole()

        self.result.update.status.borehole_changing = False

    def sample_changed(self, attr, old, new):
        if new :
            selected_sample = new
            if "." in selected_sample:
                selected_sample = selected_sample.split(".")[0]

            self.result.update.status.selected_sample = selected_sample
            if not self.result.update.status.borehole_changing:
                logger.debug('Field selected sample changed: ' + str(selected_sample))
                self.fields.log_field.log_plot.update_for_selected_sample(str(selected_sample))

                borehole_id = self.result.update.status.borehole_id
                self.result.borehole_evaluation.loc[
                    self.result.borehole_evaluation['borehole_id'] == borehole_id, 'selected_sample'] = str(selected_sample)
                logger.debug('Result selected sample changed: ' + str(selected_sample))

                try:
                    if str(selected_sample) != tlconfiguration.selected_sample_initial:
                        date = self.log_data.infos.loc[
                            (self.log_data.infos['borehole_id'] == borehole_id) & (
                                    self.log_data.infos['sample_id'].astype(str) == str(selected_sample)), 'date'].values[0]
                        self.result.borehole_evaluation.loc[
                            self.result.borehole_evaluation['borehole_id'] == borehole_id, 'date'].values[0] = date
                        logger.debug('Result date changed: ' + str(date))
                except:
                    logger.error('Failed changing date in result borehole evaluation')