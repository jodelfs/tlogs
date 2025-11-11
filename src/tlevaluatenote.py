import re
import pandas as pd
#from datetime import datetime

class EvaluateNote:
    def __init__(self, log_data, data_sources, result, log_plot):
        self.data_sources = data_sources
        self.result = result
        self.log_data = log_data
        self.log_plot = log_plot

    def execute_for_sample_note(self, note, ndx):
        sample_id = self.result.update.status.sample_list[ndx]
        # operation
        if 'ruhe' in note.lower():
            operation = 'Shut-in'
        elif 'förd' in note.lower():
            operation = 'Förderung'
        elif 'inj' in note.lower():
            operation = 'Injektion'
        else:
            operation = 'Unknown'

        self.result.update.update_sample_evaluation(sample_id, 'operation', operation)
        # water table
        match = re.search(r'wsp:\s*(\d+(\.\d+)?)\s*m', note.lower())
        if match:
            self.update_water_table(ndx, float(match.group(1)))
        # date
        match = re.search(r'datum:\s*(\d{4}-\d{2}-\d{2})', note.lower())
        if match:
            self.result.update.update_sample_evaluation(sample_id, 'date', match.group(1))#datetime.strptime(match.group(1), '%Y-%m-%d'))
        # time
        match = re.search(r'zeit:\s*(\d+(\:\d+)?)', note.lower())
        if match:
            self.result.update.update_sample_evaluation(sample_id, 'time', match.group(1))

        self.result.update.update_borehole_evaluation('static water level',
                                                      self.result.calculate_static_water_level(self.result.update.status.borehole_id))

    def execute_for_borehole_note(self, note):
        match = re.search(r'höhe:\s*(\d+(\.\d+)?)\s*m', note.lower())
        if match:
            self.result.update.update_borehole_evaluation('elevation', float(match.group(1)))

            self.log_plot.update_title()

    def update_water_table(self, ndx, water_table):
        sample_id = self.result.update.status.sample_list[ndx]

        self.result.update.update_sample_evaluation(sample_id, 'water_table', water_table)
