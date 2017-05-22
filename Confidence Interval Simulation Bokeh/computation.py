"""This module contains the ci computations."""

import numpy as np
import scipy.stats as stats
import scikits.bootstrap
import pandas as pd

def ci_anal(data, confidence=0.95):
    n = len(data)
    mean = np.mean(data)
    sem = np.std(data) / np.sqrt(n)
    interval = sem * stats.t.ppf((1 + confidence) / 2.0, n - 1)
    return np.array([mean - interval, mean + interval])


def ci_boot(data, confidence=0.95):
    return scikits.bootstrap.ci(data, alpha=1 - confidence)

def traverse(plot, past_size, future_size, ci, zoom, update=True):
    s = plot.sources
    p = plot.figure
    idx_start = plot.idx

    # index locations
    idx_end = idx_start + past_size + 1
    idx_future = idx_end + future_size

    # series values
    ser_past = s.series.iloc[idx_start:idx_end]
    ser_future = s.series.iloc[idx_end:idx_future]
    ser_entire = s.series.iloc[idx_start:idx_future]

    # x values
    x_start = ser_past.index.min()
    x_end = ser_past.index.max()
    x_future = ser_future.index.max()

    # ci lower upper
    lower, upper = ci_anal(ser_past, ci)

    # vertical bounds
    v_avg = np.mean([lower, upper])
    y_min, y_max = ser_entire.min(), ser_entire.max()
    v_max_diff = np.max([v_avg - y_min, y_max - v_avg])
    v_min = v_avg - v_max_diff
    v_max = v_avg + v_max_diff
    v_bounds = [v_min, v_max]

    # outliers
    mask = (ser_future < lower) | (ser_future > upper)
    markers = ser_future[mask]

    # updates
    if update:
        s.start.data.update({"x": [x_start] * 2, "y": v_bounds})
        s.end.data.update({"x": [x_end] * 2, "y": v_bounds})
        s.future.data.update({"x": [x_future] * 2, "y": v_bounds})
        s.ci.data.update({"x": [x_start, x_future, x_future, x_start],
                          "y": [lower, lower, upper, upper]})
        s.markers.data.update({"x": markers.index, "y": markers.values})

    if mask.all():
        data = s.marked.data
        data.update({"x": data["x"] + [x_end],
                     "y": data["y"] + [ser_past.values[-1]]})

    # x plot range
    if update:
        middle = ((idx_future - idx_start) / 2) + idx_start
        h_diff = (zoom * (past_size + future_size)) / 2
        h_min, h_max = middle - h_diff, middle + h_diff
        h_min = h_min if h_min > 0 else 0
        h_max = h_max if h_max < s.series.shape[0] - 1 else s.series.shape[0] - 1

        h_min = s.series.index.values[int(h_min)]
        h_max = s.series.index.values[int(h_max)]

        p.x_range.start = h_min
        p.x_range.end = h_max

    # table values
    table = s.table.data
    table["lower CI"] += [round(lower, 3)]
    table["upper CI"] += [round(upper, 3)]
    ts = pd.to_datetime(str(x_end))
    table["x"] += [ts.strftime('%Y.%m.%d %H:%M:%S')]
    table["mean"] += [round(ser_past.mean(), 3)]
