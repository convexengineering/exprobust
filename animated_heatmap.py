import pandas as pd
import numpy as np
import scipy.stats as stats
import itertools
import plotly.graph_objects as go

from analysis import folder_names, conditions, corrected_points


def animated_heatmap(points, condition):
    fig_dict = {
        "data": [],
        "layout": {},
        "frames": []
    }
    time_points = np.array([(points[point], *point) for point in points], dtype=[('time',int), ('perf',float), ('fail',int), ('idnum','U25')])
    time_points.sort(order="time")
    times = list(range(0, 1801, 20))
    fig_dict["layout"]["autosize"] = False
    fig_dict["layout"]["width"] = 800
    fig_dict["layout"]["height"] = 600
    fig_dict["layout"]["title"] = condition
    fig_dict["layout"]["yaxis"] = {
        "title_text": "Failure Rate",
        "range": [0,100],
        "tickmode": 'array',
        "tickvals": [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100],
        "ticktext": ["0%", "10%", "20%", "30%", "40%", "50%", "60%", "70%", "80%", "90%", "100%"]}
    fig_dict["layout"]["xaxis"] = {
        "title_text": "Fuel Consumed (lbs)",
        "range": [900,2000]
    }
    fig_dict["layout"]["sliders"] = {
        "args": [
            "transition", {
                "duration": 400,
                "easing": "cubic-in-out"
            }
        ],
        "initialValue": 0,
        "plotlycommand": "animate",
        "values": times,
        "visible": True
    }
    
    fig_dict["layout"]["updatemenus"] = [
        {
            "buttons": [
                {
                    "args": [None, {"frame": {"duration": 500, "redraw": True},
                                    "fromcurrent": True, "transition": {"duration": 300,
                                                                        "easing": "quadratic-in-out"}}],
                    "label": "Play",
                    "method": "animate"
                },
                {
                    "args": [[None], {"frame": {"duration": 0, "redraw": True},
                                      "mode": "immediate",
                                      "transition": {"duration": 0}}],
                    "label": "Pause",
                    "method": "animate"
                }
            ],
            "direction": "left",
            "pad": {"r": 10, "t": 87},
            "showactive": False,
            "type": "buttons",
            "x": 0.1,
            "xanchor": "right",
            "y": 0,
            "yanchor": "top"
        }
    ]
    
    sliders_dict = {
        "active": 0,
        "yanchor": "top",
        "xanchor": "left",
        "currentvalue": {
            "font": {"size": 20},
            "prefix": "Time (seconds): ",
            "visible": True,
            "xanchor": "right"
        },
        "transition": {"duration": 300, "easing": "cubic-in-out"},
        "pad": {"b": 10, "t": 50},
        "len": 0.9,
        "x": 0.1,
        "y": 0,
        "steps": []
    }
    x = [0] + list(np.linspace(900, 2000, 111)) + [6000]
    y = list(np.linspace(0, 100, 51))
    ticks = np.round(np.logspace(np.log10(5),np.log10(80),5))
    tick_vals = np.log(ticks)
    hmap = np.zeros((51, 112)) +.0001
    data_dict = {
        "type": "heatmap",
        "x": x,
        "y": y,
        "z": hmap,
        "zmin": -1,
        "zmax": np.log(80),
        "colorbar": {
            "tickvals": tick_vals,
            "ticktext": ticks},
        "colorscale": "magma"      
    }
    fig_dict["data"].append(data_dict)
    i = 0
    for t in times:
        frame = {"data": [], "name": str(t)}
        while i < len(time_points) and time_points["time"][i] < t:
            i+=1
        hmap = np.zeros((51, 112)) +.0001
        for _, perf, fail, _ in time_points[:i]:
            i_col = min(max(int((perf-900)/10)+1, 0), 111)
            i_row = int(fail/2)
            hmap[i_row, i_col] += 1
        hmap = np.log(hmap)
        frame["data"] = [{
            "type": "heatmap",
            "x": x,
            "y": y,
            "z": hmap,
            "zmin": -1,
            "zmax": np.log(80),
            "colorbar": {
                "tickvals": tick_vals,
                "ticktext": ticks},
            "colorscale": "magma"      
        }]
        fig_dict["frames"].append(frame)
        slider_step = {"args": [
            [t],
            {"frame": {"duration": 300, "redraw": True},
             "mode": "immediate",
             "transition": {"duration": 300}}
        ],
            "label": t,
            "method": "animate"}
        sliders_dict["steps"].append(slider_step)
    
    fig_dict["layout"]["sliders"] = [sliders_dict]
    return fig_dict

all_figs = {}
for folder_name, condition in list(zip(folder_names, conditions)):
    _, _, points, _ = corrected_points(folder_name)
    all_figs[condition] = animated_heatmap(points, condition)
    fig = go.Figure(all_figs[condition])
    fig.show()