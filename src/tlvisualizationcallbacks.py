class VisualizationCallbacks:

    def __init__(self, log_data, result, fields):
        self.log_data = log_data
        self.result = result
        self.fields = fields

    def background_changed(self, attr, old, new):
        self.fields.map_field.map_plot.update_background(new)

    def show_reports_button_clicked(self):
        if self.fields.control_field.borehole.value != '':
            self.log_data.reports.show_pdfs(self.result.update.status.borehole_id)

