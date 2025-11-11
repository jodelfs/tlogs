from tllogger import logger

class PointsCallbacks:
    def __init__(self, data_sources, log_data, result, fields):
        self.data_sources = data_sources
        self.log_data = log_data
        self.result = result
        self.fields = fields

    def point_add_clicked(self, event):
        logger.debug('Add point')

        if event.x is None or event.y is None:
            logger.debug("Klick außerhalb des Plots!")
            return
        try:
            profile = self.log_data.profiles[
                str(self.result.update.status.borehole_id) + '_' +  str(self.result.update.status.selected_sample)]
            self.result.points.add(profile, event)

            self.result.update_points()
            self.data_sources.update_points()
        except:
            logger.warning('Could not add point for ' + str(
                self.result.update.status.borehole_id) + '_' +  str(self.result.update.status.selected_sample))

    def point_delete_clicked(self, event):  # , fitting):
        logger.debug('Delete point')
        self.result.points.delete()

        self.result.update_points()
        self.data_sources.update_points()

    def all_points_delete_clicked(self, event):  # , fitting):
        logger.debug('Delete all points')
        self.fields.result.points.delete_all()

        self.result.update_points()
        self.data_sources.update_points()