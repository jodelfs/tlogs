import tlconfiguration
from tllogger import logger

from bokeh.plotting import figure
from bokeh.models import (Legend, Label,
                          Toolbar, TapTool, PanTool, BoxZoomTool, WheelZoomTool, SaveTool, BoxAnnotation)
from bokeh.palettes import Category20, Blues256, Reds256
from bokeh.models import LegendItem, MultiLine
import numpy as np

from tlmath import calculate_inflow_rate

boxes_active = []

class LogPlot:
    def __init__(self, data_sources, log_data, result, fields):

        self.p = figure(title='.',
            width=400,  # match_aspect=True,
            #active_drag="pan",
            #active_scroll="wheel_zoom"
        )

        self.data_sources = data_sources
        self.log_data = log_data
        self.result = result
        self.fields = fields

        self.p.toolbar = Toolbar(tools=[PanTool(), BoxZoomTool(), WheelZoomTool(), SaveTool()])
        self.p.toolbar.logo = None
        #self.p.toolbar_location = "above"

        self.colors = Category20[20] # used in callback

        self.line_list = list()

        for ndx in range(tlconfiguration.max_nr_logs):
            self.line_list.append(self.p.line('value', 'depth', source=data_sources.profile_list[ndx]))

        self.p.scatter('T', 'z', source=data_sources.log_water_tables, size=10, color="blue")
        self.p.scatter('T_landsat', 'z', source=data_sources.log_surface_temperature, size=10, color="green")
        self.p.scatter('T_modis', 'z', source=data_sources.log_surface_temperature, size=10, color="orange")
        self.p.scatter('T', 'z', source=data_sources.log_points_selected, size=10, color="black")

        self.p.line('T', 'z', source=data_sources.T_geothermal, color='grey', line_width=3)
        self.p.line('T', 'z', source=data_sources.T_borehole_calculated, color='black', line_width=3)

        fit_range = MultiLine(xs="T", ys="z", line_color='black', line_width=2)
        self.p.add_glyph(self.data_sources.fit_range, fit_range)

        self.fit_line = MultiLine(xs="T", ys="z", line_color='black', line_width=5, line_dash='dashed')
        self.p.add_glyph(self.data_sources.fit_line, self.fit_line)

        self.p.y_range.flipped = True
        self.p.xaxis.axis_label = "Temperature (°C)"  # X-Achsentitel
        self.p.yaxis.axis_label = "Depth (m)"  # Y-Achsentitel

        self.last_point_label = Label(x=0, y=0, text="", text_color="black", text_font_size="12pt")
        self.p.add_layout(self.last_point_label)

        self.legend = Legend(items=[]) # updated in callback
        self.legend.location = "bottom_left"  # Optionen: 'top_left', 'top_right', 'bottom_left', 'bottom_right'
        self.legend.label_text_font_size = "8pt"
        self.legend.glyph_height = 3
        self.legend.spacing = 0
        self.legend.background_fill_alpha = 0.7  # Leicht transparent machen

        self.p.add_layout(self.legend)  # , 'top_left')

        #self.make_aquifer_boxes()

    def update_aquifer_boxes_old(self):
        #try:
        if True:
            #self.p.renderers = [r for r in self.p.renderers if not isinstance(r, BoxAnnotation)] # clear old boxes
            global boxes_active
            for box in boxes_active:
                if box in self.p.center:  # BoxAnnotation hängt hier
                    self.p.center.remove(box)
            boxes_active = []

            inflow_amounts  = self.fields.note_field.get_inflow_from_text(self.fields.note_field.note_evaluation.value)
            heights = list(inflow_amounts.keys())

            if len(heights) > 0:
                heights_flat = [value for pair in heights for value in pair]
                depth_min = min(heights_flat)
                depth_max = max(heights_flat)
                logger.debug(inflow_amounts)
                logger.debug(depth_min)
                logger.debug(depth_max)
                flux = calculate_inflow_rate(depth_min, depth_max, inflow_amounts)
                logger.debug(flux)

                fmin = flux.min()
                fmax = flux.max()

                boxes_new = []
                for height in heights:
                    fval = flux[(depth_min, depth_max)] if (depth_min, depth_max) in flux else None
                    # falls du flux pro Intervall hast, direkt flux[height] nehmen

                    if fval is not None and fmax > fmin:
                        idx = int((fval - fmin) / (fmax - fmin) * (len(Blues256) - 1))
                        color = Blues256[idx]
                    else:
                        color = "lightgrey"  # fallback

                    box = BoxAnnotation(bottom=height[1], top=height[0],
                                        fill_alpha=0.6, fill_color=color)
                    self.p.add_layout(box)
                    boxes_new.append(box)

                #for height in heights:
                #    box = BoxAnnotation(bottom=height[1], top=height[0], fill_alpha=.3, fill_color='blue')
                #    self.p.add_layout(box)
                #    boxes_new.append(box)

                boxes_active = boxes_new
        #except:
        #    pass

    import numpy as np
    from bokeh.palettes import Blues256
    from bokeh.models import BoxAnnotation

    def update_aquifer_boxes(self):
        # alte Boxen löschen
        for box in getattr(self, "boxes_active", []):
            try:
                self.p.center.remove(box)
            except ValueError:
                pass
        self.boxes_active = []

        inflow_amounts = self.fields.note_field.get_inflow_from_text(
            self.fields.note_field.note_evaluation.value
        )
        heights = list(inflow_amounts.keys())

        if len(heights) > 0:
            heights_flat = [value for pair in heights for value in pair]

            flux = calculate_inflow_rate(0, #min(heights_flat)
                                         max(heights_flat), inflow_amounts)  # => Array
            #logger.debug(flux)
            fmin = 0 # (float(np.min(flux[flux>0])),
            fmax, fmax_neg = float(np.max(flux)), float(np.max(-flux))

            boxes_new = []
            for (bottom, top) in heights:
                fval = flux[bottom]
                if fval > 0:
                    idx = int(  (1 - (fval - fmin) / (fmax - fmin)) * (len(Blues256) - 40)) # 40 to make low fuxes visibe
                    color = Blues256[idx]
                elif fval < 0:
                    idx = int((1 - (-fval - fmin) / (fmax_neg - fmin)) * (len(Reds256) - 40))  # 40 to make low fuxes visibe
                    color = Reds256[idx]
                box = BoxAnnotation(bottom=bottom, top=top, fill_alpha=0.6, fill_color=color)
                self.p.add_layout(box)
                boxes_new.append(box)

            self.boxes_active = boxes_new


    def update(self):
        logger.debug('Field update - Logplot')
        borehole_id = self.result.update.status.borehole_id
        sample_list = self.result.update.status.sample_list

        self.legend.items = [LegendItem(label='', renderers=[self.line_list[ndx]]) for ndx in range(len(sample_list))]

        if len(sample_list) > tlconfiguration.max_nr_logs:
            logger.error("Not enough DataSources for logs in log plot")

        self.update_title()

        self.last_point_label.text = ''

        selected_sample = self.result.borehole_evaluation.loc[
            self.result.borehole_evaluation['borehole_id'] == borehole_id, 'selected_sample'].values[0]
        selected_sample = str(int(selected_sample)) if isinstance(selected_sample, float) else str(selected_sample)

        self.update_for_selected_sample(selected_sample)
        self.data_sources.update_points()

        for ndx, _ in enumerate(self.result.update.status.sample_list):
            self.update_sample_properties(ndx)

        self.update_aquifer_boxes()

    def update_sample_properties(self, ndx):
        borehole_id = self.result.update.status.borehole_id
        sample_id = self.result.update.status.sample_list[ndx]

        logger.debug('Field update - Logplot properties for sample ' + str(sample_id))
        # legend
        try:
            operation = self.result.sample_evaluation.loc[
                (self.result.sample_evaluation['borehole_id'] == borehole_id) & (
                        self.result.sample_evaluation['sample_id'].astype(str) == str(
                    sample_id)), 'operation'].values[0]
        except:
            operation = 'Unknown'

        try:
            date = str(self.result.sample_evaluation.loc[(self.log_data.infos['borehole_id'] == borehole_id) & (
                        self.result.sample_evaluation['sample_id'].astype(str) == str(
                    sample_id)), 'date'].values[0])[:10]
        except:
            date='0000-00-00'

        try:
            time = self.result.sample_evaluation.loc[(self.result.sample_evaluation['borehole_id'] == borehole_id) & (
                    self.result.sample_evaluation[
                        'sample_id'].astype(str) == str(sample_id)), 'time'].values[0]  # .split("_")[-1]
        except:
            time = 'Time unknown'

        self.legend.items[ndx] = LegendItem(
            label=str(sample_id) + ' ' + str(date) + ' ' + str(time) + ' ' + str(operation), renderers=[
                self.line_list[ndx]])

        # linestyle
        if operation == 'Shut-in':
            self.line_list[ndx].glyph.line_dash = []  # Durchgezogene Linie
        elif operation == 'Förderung':
            self.line_list[ndx].glyph.line_dash = [6, 6]  # Gestrichelt
        elif operation == 'Injektion':
            self.line_list[ndx].glyph.line_dash = [2, 2]  # Gepunktet
        else:  # Unknown
            self.line_list[ndx].glyph.line_dash = [6, 2, 2, 2]  # Strich-Punkt

    def update_title(self):
        borehole_id = self.result.update.status.borehole_id
        try:
            drilling_begin = str(
                self.log_data.infos.loc[self.log_data.infos['borehole_id'] == borehole_id,'drilling_begin'].values[0])
        except:
            drilling_begin = '----:--:--'
        try:
            drilling_end = str(
                self.log_data.infos.loc[self.log_data.infos['borehole_id'] == borehole_id, 'drilling_end'].values[0])
        except:
            drilling_end = '----:--:--'

        elevation = round(self.result.borehole_evaluation.loc[
                      self.result.borehole_evaluation['borehole_id'] == borehole_id, 'elevation'].values[0])
        sealing = self.log_data.infos.loc[self.log_data.infos['borehole_id'] == borehole_id, 'sealing'].values[0]
        vegetation = self.log_data.infos.loc[self.log_data.infos['borehole_id'] == borehole_id, 'vegetation'].values[0]
        land_use = self.log_data.infos.loc[self.log_data.infos['borehole_id'] == borehole_id, 'land_use'].values[0]
        land_cover = self.log_data.infos.loc[self.log_data.infos['borehole_id'] == borehole_id, 'land_cover'].values[0]
        tree_cover = self.log_data.infos.loc[self.log_data.infos['borehole_id'] == borehole_id, 'tree_cover'].values[0]
        slope = self.log_data.infos.loc[self.log_data.infos['borehole_id'] == borehole_id, 'slope'].values[0]
        aspect = self.log_data.infos.loc[self.log_data.infos['borehole_id'] == borehole_id, 'aspect'].values[0]
        try:
            land_use_text = tlconfiguration.land_use_dict[land_use]
        except:
            land_use_text = ''

        try:
            land_cover_text = tlconfiguration.land_cover_dict[land_use][land_cover]
        except:
            land_cover_text = ''

        title_text = (str(borehole_id) + ' / ' + str(self.log_data.infos.loc[
            self.log_data.infos['borehole_id'] == borehole_id, 'report_reference'].values[0]) + '\n' +
                      str(elevation) + f' m ASL (Slope: {slope:.1f} %, Aspect: {aspect:.0f} °)\nSealing: ' +
                      f'{sealing:.0f}' + ', Trees: ' + f'{tree_cover:.0f}' +
                      ' % (Vegetation: ' + str(vegetation)  + ' %)\n' +
                      str(land_use) + ' / ' + str(land_cover) + '\n' +
                      str(land_use_text) + ' - ' + str(land_cover_text) +
                      '\nDrilling: ' + str(drilling_begin) + ' - ' + str(drilling_end))
        logger.debug('Field update - Logplot title: ' + str(title_text)[:tlconfiguration.debug_note_length])
        self.p.title.text = title_text

    def update_for_selected_sample(self, selected_sample):
        sample_list = self.result.update.status.sample_list
        logger.debug('Field update -  Logplot line color for selected sample: ' + str(selected_sample))
        for ndx, sample in enumerate(sample_list):
            # color, linewidth
            if str(sample) == selected_sample:
                self.line_list[ndx].glyph.line_color = "red"
                self.line_list[ndx].glyph.line_width = 5
            else:
                self.line_list[ndx].glyph.line_color = self.colors[ndx%20]
                self.line_list[ndx].glyph.line_width = 3


