"""This module handles the view and model interactions."""

import time
from bokeh.io import curdoc
from threading import Thread

import view
import model
import computation

doc = curdoc()

LOOP_TIME = 1000

class PlotContainer:
    def __init__(self, figure, sources, idx=0):
        self.figure = figure
        self.sources = sources
        self.idx = idx

table_cols = ("x", "lower CI", "upper CI", "mean")
cfg = dict()

sources = model.sources()
v_tabs = view.Plots(sources, cfg)
v_settings = view.Settings(cfg)
v_control = view.Control(cfg)

table_source = model.table_source(True)
v_table = view.Table(table_source)

v_view = view.build_view(v_control.layout,
                         v_settings.layout,
                         v_tabs.layout,
                         v_table.layout)

plots = [PlotContainer(figure, sources, 0)
         for figure, sources in zip(v_tabs.plots, sources)]


def start_thread(target):
    def wrapper():
        thread = Thread(target=step_all)
        thread.start()
    return wrapper


def loopable():
    cur_plot = plots[cfg["tab"]]
    window = cfg["past_size"] + cfg["future_size"]
    return cur_plot.idx < cur_plot.sources.series.shape[0] - window - 1


def main_loop():
    if cfg["on_off"] == 0:
        step_runs()


def step_all():
    while loopable():
        step_single(False)

    cur_plot = plots[cfg["tab"]]
    cur_plot.sources.update()

def step_runs():
    sleep_time = (LOOP_TIME-200) / cfg["speed"] / 1000.0
    steps = cfg["speed"]

    for _ in range(steps):
        step_single()
        time.sleep(sleep_time)


def step_single(update=True):
    cur_plot = plots[cfg["tab"]]
    computation.traverse(cur_plot,
                         cfg["past_size"],
                         cfg["future_size"],
                         cfg["ci"],
                         cfg["zoom"],
                         update)
    cur_plot.idx += 1
    cur_plot.sources.update()
    table_source.data = cur_plot.sources.table.data


def reset():
    plot = plots[cfg["tab"]]
    plot.sources.reset()
    plot.idx = 0
    plot.figure.x_range.start = plot.sources.series.index.min()
    plot.figure.x_range.end = plot.sources.series.index.max()


# add callbacks
v_control.step_single.on_click(step_single)
v_control.step_all.on_click(step_all)
v_control.reset.on_click(reset)


doc.add_root(v_view)
doc.title = "Predictive Calls"
curdoc().add_periodic_callback(main_loop, LOOP_TIME)
