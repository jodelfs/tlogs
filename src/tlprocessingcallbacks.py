from tlexport import Export
from bokeh.plotting import curdoc

class ProcessingCallbacks:
    def __init__(self, log_data, result, fields):
        self.log_data = log_data
        self.result = result
        self.fields = fields

    def store_button_clicked(self):
        self.fields.log_field.store.label = "Storing ..."
        #export = Export(self.result, self.log_data.infos, self.fields)
        curdoc().add_next_tick_callback(self.export_results)

    def export_results(self):
        export = Export(self.log_data, self.result)
        export.execute()

        self.fields.log_field.store.label = "Store in file & DB"

    def result_method_selected(self, attr, old, new):
        self.result.update.update_fitting('selected_method', new)
