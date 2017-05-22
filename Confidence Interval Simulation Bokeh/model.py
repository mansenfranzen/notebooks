"""This module contains the data handler."""

import numpy as np
import tssim

from bokeh.models import ColumnDataSource


def create_source(series):
    return ColumnDataSource(data=dict(x=series.index.values, y=series.values))

def dummy1():
    ts = tssim.TimeSeries(start="2017-04-04", freq="D", periods=1100)
    ts.add("Noise", lambda x: x * 0 + np.random.normal(0, 0.25, size=x.shape[0]))
    ts.add("Log", lambda x: np.log(x))
    ts.add("Increase", lambda x: x * 0.01, condition=lambda x: x < 1)
    return ts.generate().values

def dummy2():
    ts = tssim.TimeSeries(start="2017-04-04", freq="D", periods=1100)
    ts.add("Noise", lambda x: x * 0 + np.random.normal(0, 0.25, size=x.shape[0]))
    return ts.generate().values

def sources():
    return [PlotData("Mixed", dummy1()),
            PlotData("Noise", dummy2())]

def table_source(source=False):
    columns = ("x", "lower CI", "upper CI", "mean")
    result = {column: [] for column in columns}

    if source:
        return ColumnDataSource(result)
    else:
        return result

class DataSource:
    def __init__(self, data):
        self.data = data
        self.sync = ColumnDataSource(self.data)

    def update(self):
        self.sync.data = self.data


class PlotData:
    def __init__(self, label, series):
        self.label = label
        self.series = series
        self.source = create_source(series)

        empty = dict(x=[], y=[])
        self.start = DataSource(empty.copy())
        self.end = DataSource(empty.copy())
        self.future = DataSource(empty.copy())
        self.markers = DataSource(empty.copy())
        self.marked = DataSource(empty.copy())
        self.ci = DataSource(empty.copy())
        self.table = DataSource(table_source())

    def update(self):
        to_update = ("start", "end", "future", "markers", "marked", "ci", "table")
        for item in to_update:
            getattr(self, item).update()

    def reset(self):
        empty = dict(x=[], y=[])
        self.start.data.update(empty.copy())
        self.end.data.update(empty.copy())
        self.future.data.update(empty.copy())
        self.markers.data.update(empty.copy())
        self.marked.data.update(empty.copy())
        self.ci.data.update(empty.copy())
        self.table.update(table_source())
        self.update()

