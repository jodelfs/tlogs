import tlconfiguration
from tlevaluatenote import EvaluateNote
from tllogger import logger

from bokeh.layouts import row, column
from bokeh.models import Div, TextAreaInput

import re
import numpy as np
import pandas as pd

def extract_ranges(text):
    ranges = dict()

    # Regulärer Ausdruck, um Zahlen, "ab", "bis", "all" und Durchflussraten zu extrahieren
    flow_pattern = r"(ab |bis |all: )?(\d+(?:-\d+)?): (-?[\d.]+)"

    # Extraktion der Höhen und Raten
    flow_matches = re.findall(flow_pattern, text)

    for match in flow_matches:
        ab_bis_all, hoehe, value = match

        # Wenn "ab" oder "bis" oder "all" vorhanden ist, behandeln wir diese Fälle
        if ab_bis_all == "ab ":
            # Wenn "ab" vorkommt, setze die obere Grenze auf 10000
            ranges[(int(hoehe), 10000)] = float(value)
        elif ab_bis_all == "bis ":
            # Wenn "bis" vorkommt, setze die untere Grenze auf 0
            ranges[(0, int(hoehe))] = float(value)
        elif ab_bis_all == "all: ":
            # Wenn "all" vorkommt, setze es für alle Höhen (hier als spezieller Schlüssel)
            ranges[(0, 10000)] = float(value)  # all bezieht sich auf den Bereich 0-10000
        elif "-" in hoehe:  # Fall Bereich (z. B. "120-121")
            unten, oben = map(int, hoehe.split("-"))
            ranges[(unten, oben)] = float(value)
        else:  # Einzelne Zahl (z. B. "88")
            unten = int(hoehe)
            ranges[(unten, unten + 1)] = float(value)

    return ranges


class NoteField:
    def __init__(self, data_sources, result, log_data, log_plot):
        self.data_sources = data_sources
        self.result = result
        self.log_data = log_data

        self.note_evaluation = TextAreaInput(value="", title="Evaluation", width=300, height=200)
        self.note_borehole = TextAreaInput(value="", title="Borehole", width=300, height=200)

        self.note_sample_list = [TextAreaInput(
            value="", title=".", width=300, height=60)  for _ in range(tlconfiguration.max_nr_logs)]

        self.evaluate_note = EvaluateNote(self.log_data, self.data_sources, self.result, log_plot)

    def update_for_borehole(self):
        self.note_evaluation.value = '' if pd.isna(self.result.get_field_value_for_borehole('note_evaluation')) else self.result.get_field_value_for_borehole('note_evaluation')
        self.note_borehole.value = '' if pd.isna(self.result.get_field_value_for_borehole('note_borehole')) else self.result.get_field_value_for_borehole('note_borehole')

        borehole_id, sample_list = self.result.update.status.borehole_id, self.result.update.status.sample_list

        #print(self.result.sample_evaluation.columns)

        for ndx, sample in enumerate(sample_list):
            self.note_sample_list[ndx].title = 'Sample ' + str(sample)
            try:
                global_sample_id = borehole_id + '_' + str(sample)
                sample_note = self.result.sample_evaluation.loc[self.result.sample_evaluation['global_sample_id'] == global_sample_id, 'note_sample'].values[0]
                if pd.isna(sample_note):
                    sample_note = ''
                logger.debug('Field update - sample ' + str(
                    sample) + ': ' + str(sample_note[
                                               :tlconfiguration.debug_note_length].replace('\n', ' ')))
                self.note_sample_list[ndx].value = sample_note
            except:
                logger.error('Update sample note failed')

        for ndx in range(len(sample_list), tlconfiguration.max_nr_logs):
            self.note_sample_list[ndx].title = '.'
            self.note_sample_list[ndx].value = ''

    def update_note_sample(self, note, ndx):
        self.result.update.update_sample_evaluation(self.result.update.status.sample_list[ndx], 'note_sample', note)
        self.evaluate_note.execute_for_sample_note(note, ndx)

    def note_borehole_changed(self, note):
        self.result.update.update_borehole_evaluation('note_borehole', note)
        self.evaluate_note.execute_for_borehole_note(note)

    def get_inflow_from_text(self, text):
        pattern = r"Zufluss:\s*(.*?)(?:;|$)"
        matches = re.findall(pattern, text)
        inflow = {}

        # Überprüfe, ob Übereinstimmungen gefunden wurden
        if matches:
            # Extrahiere den relevanten Teil nach "Zufluss:"
            inflow = extract_ranges(matches[0])

        #####
        logger.debug('Calculation update - Inflow: ' + str(inflow))
        return inflow

    def get_input_for_calculation(self):
        evaluation_text = self.note_evaluation.value
        inflow = self.get_inflow_from_text(evaluation_text)

        pattern = r"Gradient:\s*(.*?)(?:;|$)"
        matches = re.findall(pattern, evaluation_text)
        gradient_geothermal = {}

        # Überprüfe, ob Übereinstimmungen gefunden wurden
        if matches:
            # Extrahiere den relevanten Teil nach "Zufluss:"
            gradient_geothermal = extract_ranges(matches[0])

            logger.debug('Calculation update - Gradient: ' + str(gradient_geothermal))

        pattern = r"Leitwert: (-?[\d.]+)"
        matches = re.findall(pattern, evaluation_text)

        conductance_thermal = np.nan

        if matches:  # T_grad
            conductance_thermal = float(matches[0])
            logger.debug('Calculation update - Conductance: ' + str(conductance_thermal))
        #####

        pattern = r"Korrektur:\s*(-?[\d.]+)"
        matches = re.findall(pattern, evaluation_text)

        correction_thermal = np.nan, np.nan

        if matches:  # T_grad
            correction_thermal = float(matches[0])
            logger.debug('Calculation update - Correction: ' + str(correction_thermal))


        return inflow, gradient_geothermal, conductance_thermal, correction_thermal


    def field(self):
        return column([self.note_evaluation
                          , self.note_borehole
                          #,self.text_field
                      ] + self.note_sample_list)
