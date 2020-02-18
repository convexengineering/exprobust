import pandas as pd
import numpy as np
import scipy.stats as stats
import scipy.spatial as spatial
import itertools
import plotly.graph_objects as go

from analysis import folder_names, conditions, corrected_points


def animated_heatmap(time_points, times, condition):
    fig_dict = {
        "data": [],
        "layout": {},
        "frames": []
    }
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
    prev_i = 0
    hmap = np.zeros((51, 112)) +.0001
    for t in times:
        frame = {"data": [], "name": str(t)}
        while i < len(time_points) and time_points["time"][i] < t:
            i+=1
        for _, perf, fail, _ in time_points[prev_i:i]:
            i_col = min(max(int((perf-900)/10)+1, 0), 111)
            i_row = int(fail/2)
            hmap[i_row, i_col] += 1
        prev_i = i
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


def animated_convex_hull(chulls, times, condition):
    fig_dict = {
        "data": [],
        "layout": {},
        "frames": []
    }
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
    data_dict = {
        "type": "scatter",
        "x": [],
        "y": [],
        "mode": "lines+markers"
    }
    fig_dict["data"].append(data_dict)
    for i in range(len(times)):
        t = times[i]
        hull = chulls[i]
        x = hull.points[hull.vertices,0]
        x = np.append(x, hull.points[hull.vertices,0][0])
        y = hull.points[hull.vertices,1]
        y = np.append(y, hull.points[hull.vertices,1][0])
        frame = {"data": [], "name": str(t)}
        frame["data"] = [{
            "type": "scatter",
            "x": x,
            "y": y,
            "mode": "lines+markers"
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


def convex_hull_time(time_points, times, condition):
    convex_hulls = []
    areas = []
    norm_areas_ver = []
    norm_areas_hor = []
    this_time_points = []
    i = 0
    prev_i = 0
    min_fail = 100
    max_fail = 0
    min_perf = 5000
    max_perf = 0
    for t in times:
        while i < len(time_points) and time_points["time"][i] < t:
            min_fail = time_points["fail"][i] if min_fail > time_points["fail"][i] else min_fail
            max_fail = time_points["fail"][i] if max_fail < time_points["fail"][i] else max_fail
            min_perf = time_points["perf"][i] if min_perf > time_points["perf"][i] else min_perf
            max_perf = time_points["perf"][i] if max_perf < time_points["perf"][i] else max_perf
            i+=1
        this_time_points.extend([(perf, fail) for _, perf, fail, _ in time_points[prev_i:i]])
        prev_i = i
        try:
            convex_hulls.append(spatial.ConvexHull(this_time_points))
            areas.append(convex_hulls[-1].area)
            norm_areas_ver.append(areas[-1]/(max_perf-min_perf))
            norm_areas_hor.append(areas[-1]/(max_fail-min_fail))
        except Exception:
            fake_chull = lambda: None
            setattr(fake_chull, 'area', 0)
            setattr(fake_chull, 'points', np.array([[0,0],[0,0]]))
            setattr(fake_chull, 'vertices', np.array([0,0]))
            convex_hulls.append(fake_chull)
            areas.append(0)
            norm_areas_ver.append(0)
            norm_areas_hor.append(0)
    return convex_hulls, areas, norm_areas_ver, norm_areas_hor

    
def plot_all_over_time(all_data, stat_name, times):
    fig = go.Figure(
        data=[go.Scatter(
            x=times,
            y=all_data[condition],
            marker=dict(
                size=6,
                opacity=0.6),
            mode="lines",
            name=condition) for condition in all_data],
        layout_title_text=stat_name)
    fig.update_layout(
        autosize=False,
        width=800,
        height=600,
        showlegend=True,
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=go.layout.XAxis(
            title_text="Time (seconds)",
        ),
        yaxis=go.layout.YAxis(
            title_text=stat_name,
            ticks="outside",
            gridcolor='rgba(0,0,0,.1)'
        )
    )
    fig.show()


def plot_avg_over_time(all_data, stat_name, times):
    fig = go.Figure(
        data=[go.Scatter(
            x=times,
            y=np.mean(list(all_data[condition].values()), axis=0),
            marker=dict(
                size=6,
                opacity=0.6),
            mode="lines",
            name=condition) for condition in all_data],
        layout_title_text=stat_name)
    fig.update_layout(
        autosize=False,
        width=800,
        height=600,
        showlegend=True,
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=go.layout.XAxis(
            title_text="Time (seconds)",
        ),
        yaxis=go.layout.YAxis(
            title_text=stat_name,
            ticks="outside",
            gridcolor='rgba(0,0,0,.1)'
        )
    )
    fig.show()


if __name__ == "__main__":
    all_figs = {}
    all_areas = {condition: {} for condition in conditions}
    all_norm_areas_ver = {condition: {} for condition in conditions}
    all_norm_areas_hor = {condition: {} for condition in conditions}
    # times = list(range(0, 1801, 20))
    times = list(range(1, 1801, 20))
    dtype = [('time',int), ('perf',float), ('fail',int), ('idnum','U25')]
    for folder_name, condition in list(zip(folder_names, conditions)):
        _, _, points, _ = corrected_points(folder_name)
        time_points = np.array([(points[point], *point) for point in points], dtype=[('time',int), ('perf',float), ('fail',int), ('idnum','U25')])
        # for idnum in np.unique(time_points["idnum"]):
        #     this_time_points = np.array([time_point for time_point in time_points if time_point["idnum"] == idnum], dtype=dtype)
        #     chulls, areas, norm_areas_ver, norm_areas_hor = convex_hull_time(this_time_points, times, condition)
        #     all_areas[condition][idnum] = areas
        #     all_norm_areas_ver[condition][idnum] = norm_areas_ver
        #     all_norm_areas_hor[condition][idnum] = norm_areas_hor

        # time_points.sort(order="time")
        # all_figs[condition] = animated_heatmap(time_points, times, condition)
        # fig = go.Figure(all_figs[condition])
        # fig.show()
        
        time_points.sort(order="time")
        chulls, areas, norm_areas_ver, norm_areas_hor = convex_hull_time(time_points, times, condition)
        all_areas[condition] = areas
        all_norm_areas_ver[condition] = norm_areas_ver
        all_norm_areas_hor[condition] = norm_areas_hor
        go.Figure(animated_convex_hull(chulls, times, condition)).show()

    # plot_avg_over_time(all_areas, "Area of Convex Hull", times)
    # plot_avg_over_time(all_norm_areas_ver, "Normalized Area of Convex Hull by Performance", times)
    # plot_avg_over_time(all_norm_areas_hor, "Normalized Area of Convex Hull by Failure Rate", times)

    # plot_all_over_time(all_areas, "Area of Convex Hull", times)
    # plot_all_over_time(all_norm_areas_ver, "Normalized Area of Convex Hull by Performance", times)
    # plot_all_over_time(all_norm_areas_hor, "Normalized Area of Convex Hull by Failure Rate", times)