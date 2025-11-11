
class QualityCallbacks:
    def __init__(self, data_sources, result):
        self.data_sources = data_sources
        self.result = result

    def quality_judgement_field_changed(self,
                                      field, # quality, drillingInduced, deactivated
                                      attr, old, new
                                      ):
        if (self.result.update.status.borehole_id != '' and
                not self.result.update.status.borehole_changing):
            self.result.update.update_borehole_evaluation(field, new)

            self.data_sources.update_map_boreholes_for_quality()

    def info_slider_changed(self, info_field, attr, old, new):
        self.result.update.update_borehole_evaluation(info_field, new)
