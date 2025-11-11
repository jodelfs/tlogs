from bokeh.layouts import column
from bokeh.models import AutocompleteInput, Select

class SelectionField:
    def __init__(self, infos_unique):
        self.borehole = AutocompleteInput(title="Select borehole",
                                          completions=list(infos_unique['borehole_id']),
                                          min_characters=1)
        self.sample = Select(title="Select sample:", value="0", options=["0"])

    def field(self):
        return column([self.borehole, self.sample])