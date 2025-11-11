import tlpoints
from bokeh.layouts import row, column
from bokeh.models import Button, Checkbox

class PointField:
    def __init__(self, data_sources, result, log_plot):

        self.delete_point = Button(label="Delete point", button_type="danger")
        self.delete_all_points = Button(label="Delete all points", button_type="danger")
        self.attach_to_sample = Checkbox(label="Attach to sample", active=True)

        self.points = tlpoints.Points(data_sources, result, log_plot, self.attach_to_sample)

    def field(self):
        return column([self.delete_point, self.delete_all_points, self.attach_to_sample])