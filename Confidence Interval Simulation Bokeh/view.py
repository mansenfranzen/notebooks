"""This module contains the user interface components including buttons,
sliders, plots etc.

"""

from bokeh.plotting import figure
from bokeh.layouts import layout, Spacer
from bokeh.palettes import Greens4

from bokeh.models.widgets import DataTable, DateFormatter, TableColumn, \
    RadioButtonGroup, Slider, Panel, Tabs, TextInput, Button, Div

VERT_CFG = {"color": "grey", "line_dash": "dotted", "line_width": 2,
            "legend": "Past Size"}
VERTF_CFG = {"line_dash": "dotted", "line_width": 2, "legend": "Future Size",
             "color": "blue"}

CI_CFG = {"alpha": 0.2, "fill_color": Greens4[1], "line_color": Greens4[0],
          "line_alpha": 1, "fill_alpha": 0.2, "legend": "CI Interval"}


def setup_link(element, attribute, label, cfg):
    cfg[label] = element.__getattribute__(attribute)

    def _pass_change(attr, old, new):
        cfg[label] = new
        print(cfg)

    element.on_change(attribute, _pass_change)


class Control:
    def __init__(self, cfg, width=200):
        self.title = Div(text="<h3>Controls</h3>")
        self.step_single = Button(label="Single step", width=int(width / 2))
        self.step_all = Button(label="All steps", width=int(width / 2))
        self.on_off = RadioButtonGroup(labels=["Run", "Stop"],
                                       active=1, width=int(width / 2))
        self.speed = Slider(start=1, end=10, value=1, step=1,
                            title="Steps per second", width=width)
        self.reset = Button(label="Reset", width=int(width / 2))
        self.zoom = Slider(start=1, end=5, value=2.5, step=0.5, title="Zoom",
                           width=width)

        setup_link(self.on_off, "active", "on_off", cfg)
        setup_link(self.speed, "value", "speed", cfg)
        setup_link(self.zoom, "value", "zoom", cfg)

    @property
    def layout(self):
        return layout([[self.title],
                       [self.step_single, self.step_all],
                       [self.on_off, self.reset],
                       [self.speed],
                       [self.zoom]])


class Settings:
    def __init__(self, cfg, width=200):
        self.title = Div(text="<h3>Settings</h3>")

        self.past_size = Slider(start=20, end=100, value=30, step=1,
                                title="Past Size", width=width)
        self.future_size = Slider(start=1, end=15, value=7, step=1,
                                  title="Future Size", width=width)
        self.ci = Slider(start=0, end=1, value=0.95, step=0.01,
                         title="Confidence Interval", width=width)

        setup_link(self.past_size, "value", "past_size", cfg)
        setup_link(self.future_size, "value", "future_size", cfg)
        setup_link(self.ci, "value", "ci", cfg)

    @property
    def layout(self):
        return layout([[self.title],
                       [self.past_size],
                       [self.future_size],
                       [self.ci]])


class Plots:
    def __init__(self, plot_sources, cfg, width=900):
        self.plots = []

        panels = []
        for sources in plot_sources:
            p = figure(width=width, x_axis_type="datetime",
                       x_range=[sources.series.index.min().timestamp() * 1000,
                                sources.series.index.max().timestamp() * 1000])
            p.patch("x", "y", source=sources.ci.sync, **CI_CFG)
            p.line("x", "y", source=sources.source)
            p.line("x", "y", source=sources.start.sync, **VERT_CFG)
            p.line("x", "y", source=sources.end.sync, **VERT_CFG)
            p.line("x", "y", source=sources.future.sync, **VERTF_CFG)
            p.circle("x", "y", source=sources.marked.sync, color="orange",
                     legend="Past Crit.")
            p.circle("x", "y", source=sources.markers.sync, color="red",
                     legend="Current Crit.")

            self.plots.append(p)
            panels.append(Panel(child=p, title=sources.label))

        self.tabs = Tabs(tabs=panels)

        setup_link(self.tabs, "active", "tab", cfg)

    @property
    def layout(self):
        return self.tabs


class Table:
    def __init__(self, source):
        self.columns = [TableColumn(field=x, title=x)
                        for x in source.data.keys()]
        self.source = source

    @property
    def layout(self):
        return DataTable(source=self.source, columns=self.columns)


def build_view(control, setting, tabs, table):
    return layout([[setting, Spacer(width=50), control],
                   [tabs],
                   [table]])
