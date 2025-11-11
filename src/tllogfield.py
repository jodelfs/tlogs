from tllogplot import LogPlot


from bokeh.models import Button, Spacer
from bokeh.layouts import row, column

class LogField:
    def __init__(self, data_sources, log_data, result, fields):
        self.log_plot = LogPlot(data_sources, log_data, result, fields)
        self.reset_button = Button(label="Reset Log", button_type="warning")

        self.show_reports_button = Button(label="Show reports", button_type="success")
        self.store = Button(label="Store in file & DB", button_type="success")

    def field(self):
        row1 = row([self.reset_button, self.show_reports_button, Spacer(width=35), self.store])
        return column([row1,
                       self.log_plot.p])