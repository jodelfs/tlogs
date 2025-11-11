from bokeh.models import Button, RangeSlider
from bokeh.layouts import row, column

class StoreField:
    def __init__(self):
        self.store = Button(label="Store in file & DB", button_type="success")

        self.fit_slider = RangeSlider(start=0, end=0, value=(0, 0), step=1, title="Tit range")

    def field(self):
        return column([self.store, self.fit_slider])