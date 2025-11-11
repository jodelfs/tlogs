import tlconfiguration
from tlselectioncallbacks import SelectionCallbacks
from tlqualitycallbacks import QualityCallbacks
from tlnotecallbacks import NoteCallbacks
from tlprocessingcallbacks import ProcessingCallbacks
from tlvisualizationcallbacks import VisualizationCallbacks
from tlpointscallbacks import PointsCallbacks
from tlcalculationcallbacks import CalculationCallbacks
from tlfitcallbacks import FitCallbacks

from bokeh.models import CustomJS
from bokeh.events import Tap
from functools import partial

class Events:
    def __init__(self, data_sources, log_data, infos_unique, result, fields):
        self.data_sources = data_sources
        self.log_data = log_data
        self.infos_unique = infos_unique

        self.status = result.update.status
        self.result = result
        self.fields = fields

        self.selection_callbacks = SelectionCallbacks(data_sources, log_data, infos_unique, result, fields)
        self.quality_callbacks = QualityCallbacks(data_sources, result)
        self.note_callbacks = NoteCallbacks(data_sources, result, fields)
        self.processing_callbacks = ProcessingCallbacks(log_data, result, fields)
        self.visualization_callbacks = VisualizationCallbacks(log_data, result, fields)

        self.points_callbacks = PointsCallbacks(data_sources, log_data, result, fields)
        self.calculation_callbacks = CalculationCallbacks(data_sources, log_data, result, fields)
        self.fit_callbacks = FitCallbacks(data_sources, log_data, result, fields)

        # selection callbacks
        self.data_sources.map_boreholes.selected.on_change("indices", self.selection_callbacks.clicked_on_map)
        self.fields.control_field.borehole.on_change("value", self.selection_callbacks.borehole_selection_field_changed)
        self.fields.control_field.sample.on_change('value', self.selection_callbacks.sample_changed)

        # quality callbacks
        self.fields.control_field.quality.on_change(
            'value', partial(self.quality_callbacks.quality_judgement_field_changed, 'quality'))
        self.fields.control_field.drilling_induced.on_change(
            "active", partial(self.quality_callbacks.quality_judgement_field_changed, 'drillingInduced'))
        self.fields.control_field.deactivated.on_change(
            "active", partial(self.quality_callbacks.quality_judgement_field_changed, 'deactivated'))

        self.fields.control_field.flow_info_slider.on_change(
            'value', partial(self.quality_callbacks.info_slider_changed, 'flow_info'))
        self.fields.control_field.time_info_slider.on_change(
            'value', partial(self.quality_callbacks.info_slider_changed, 'time_info'))
        self.fields.control_field.borehole_info_slider.on_change(
            'value', partial(self.quality_callbacks.info_slider_changed, 'borehole_info'))
        self.fields.control_field.lithology_info_slider.on_change(
            'value', partial(self.quality_callbacks.info_slider_changed, 'lithology_info'))

        # note callbacks
        self.fields.note_field.note_evaluation.on_change('value', self.note_callbacks.note_evaluation_changed)
        self.fields.note_field.note_borehole.on_change('value', self.note_callbacks.note_borehole_changed)

        for ndx in range(tlconfiguration.max_nr_logs):
            self.fields.note_field.note_sample_list[ndx].on_change(
                'value', partial(self.note_callbacks.note_sample_changed, ndx=ndx))
        # processing callbacks
        self.fields.log_field.store.on_click(self.processing_callbacks.store_button_clicked)
        self.fields.control_field.method_selection.on_change(
            'active', self.processing_callbacks.result_method_selected)
        # visualization callbacks
        self.fields.map_field.background_selection.on_change(
            "active", self.visualization_callbacks.background_changed)
        self.fields.log_field.show_reports_button.on_click(
            self.visualization_callbacks.show_reports_button_clicked)

        self.fields.map_field.reset_button.js_on_click(
            CustomJS(args=dict(p=self.fields.map_field.map_plot.p), code="p.reset.emit();"))
        self.fields.log_field.reset_button.js_on_click(
            CustomJS(args=dict(p=self.fields.log_field.log_plot.p), code="p.reset.emit();"))
        # pnts
        self.fields.log_field.log_plot.p.on_event(Tap, self.points_callbacks.point_add_clicked) # control
        self.fields.control_field.delete_point.on_click(self.points_callbacks.point_delete_clicked)  # control
        self.fields.control_field.delete_all_points.on_click(self.points_callbacks.all_points_delete_clicked) # deleta all

        # cac
        self.fields.control_field.calculation_checkbox.on_change("active", self.calculation_callbacks.calculation_checkbox_changed) # switch
        self.fields.control_field.calculation_button.on_click(self.calculation_callbacks.calculation_button_clicked) # exec
        self.fields.control_field.delete_calc_button.on_click(self.calculation_callbacks.delete_calc_button_clicked) # delete all

        #  fit
        self.fields.control_field.fit_checkbox.on_change("active", self.fit_callbacks.fit_checkbox_changed) # switch
        self.fields.control_field.fit_button.on_click(self.fit_callbacks.fit_button_clicked) # exec
        self.fields.control_field.fit_slider.on_change('value', self.fit_callbacks.update_fit_range) # control
        self.fields.control_field.delete_fit_button.on_click(self.fit_callbacks.delete_fit_button_clicked) # delete all
