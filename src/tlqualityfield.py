from bokeh.layouts import row, column
from bokeh.models import Spinner, Checkbox

class QualityField:
    def __init__(self):
        self.quality = Spinner(title="Log quality", low=-1, high=3, step=1, value=None)
        self.drilling_induced = Checkbox(label="Drilling Induced", active=False)
        self.deactivated = Checkbox(label="Deactivate", active=False)

    def field(self):
        row_checkboxes = row([self.deactivated, self.drilling_induced])
        return column([self.quality, row_checkboxes])