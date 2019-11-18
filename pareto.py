import os
import pickle
import pandas as pd
import plotly.graph_objects as go
from monte_carlo import monte_carlo_results
from simpleac import SimPleAC


def save_point(point_path, point_end="_point.txt", model_gen=SimPleAC, seed=246):
    with open(point_path, "rb") as f:
        sol = pickle.load(f)
        perf, fail = monte_carlo_results(model_gen(), sol=sol, quiet=True, seed=seed)
    with open(point_path + point_end, "w") as f:
        f.write("unknown\n")
        f.write(str(perf)+", "+str(fail))
    return perf, fail


def get_points(folder_name, point_end="_point.txt", model_gen=SimPleAC, seed=246):
    pointids = {}
    idpoints = {}
    ids = sorted(os.listdir(folder_name))
    for subject in ids:
        idpoints[subject] = []
        subj_path = folder_name + subject
        subj_points = sorted([x for x in os.listdir(subj_path)
                         if not x.endswith(".txt")], key = int)
        for subj_point in subj_points:
            point_path = subj_path + "/" + subj_point
            if os.path.isfile(point_path + point_end):
                with open(point_path + point_end, "r") as f:
                    pf_line = f.readlines()[1]
                    perf, fail = [float(x) for x in pf_line.split(", ")]
            else:
                perf, fail = save_point(point_path, point_end=point_end, model_gen=model_gen, seed=seed)
            if (perf, fail) in pointids:
                if subject not in pointids[(perf, fail)]:
                    pointids[(perf, fail)].append(subject)
            else:
                pointids[(perf, fail)] = [subject]
            idpoints[subject].append((perf,fail))
    return pointids, idpoints


def count_regions(idpoints):
    regions = {}
    for idnum in idpoints:
        regions[idnum] = 0
        in_green = False
        in_blue = False
        in_yellow = False
        for point in idpoints[idnum]:
            perf, fail = point
            if (not in_green and (perf <= 1200 and fail <= 30)):
                regions[idnum] += 1
                in_green = True
            elif (not in_yellow and (perf <= 2000 and fail <= 10)):
                regions[idnum] += 1
                in_yellow = True
            elif (not in_blue and (perf <= 1100)):
                regions[idnum] += 1
                in_blue = True
            if in_green and (in_blue and in_yellow):
                break
    return regions


# pareto_points = [((perf, fail), [id#, ...]), ...]
def pareto(pointids):
    pareto_points = {}
    for point in pointids:
        perf, fail = point
        im_pareto = True
        im_not_pareto = []
        same = None
        for pareto_point in pareto_points:
            if (pareto_point[0] <= perf and pareto_point[1] <= fail):
                im_pareto = False
                break
            elif (pareto_point[0] >= perf and pareto_point[1] >= fail):
                im_not_pareto.append(pareto_point)
        if im_pareto:
            pareto_points[point] = pointids[point]
            for not_pareto_point in im_not_pareto:
                pareto_points.pop(not_pareto_point)
    return pareto_points


def heatmap_points(points, title):
    x, y = list(zip(*points.keys()))
    colors = [len(ids) for ids in points.values()]
    #xy, colors = list(zip(*points))
    #colors = [len(color) for color in colors]
    #x, y = list(zip(*xy))
    fig = go.Figure(
        data=[go.Scatter(
            x=x, 
            y=y, 
            marker=dict(
                size=12,
                color=colors,
                opacity=0.8,
                colorbar=dict(title="Colorbar"),
                colorscale="plasma"),
            mode="markers")],
        layout_title_text=title)
    fig.show()


def compensation(pareto_points, regions, idfile, outfile):
    pareto_money = 20
    base_money = 20
    per_region = 3
    all_3 = 1
    per_point = pareto_money/len(pareto_points)
    comp = {}
    for idnum in regions:
        comp[idnum] = base_money + regions[idnum] * per_region
        if regions[idnum] == 3:
            comp[idnum] += 1
    for pareto_point in pareto_points:
        ids = pareto_points[pareto_point]
        point_divide = len(ids)
        for idnum in ids:
            comp[idnum] += per_point/point_divide
    output = []
    idf = pd.read_excel(idfile, index_col=2)
    for idnum in comp:
        int_id = int(idnum.split(" (ID ")[1][:-1])
        output.append([idf.loc[int_id, "Email"], round(comp[idnum],2)])
    odf = pd.DataFrame(data=output, columns=["Email", "Dollars"])
    with pd.ExcelWriter(outfile) as writer:
        odf.to_excel(writer)


def fragility(folder_name, title, model_gen=SimPleAC, seed=358):
    point_end = "_frag%i.txt" %seed
    pointids, idpoints = get_points(folder_name, point_end, model_gen, seed)
    pps = pareto(pointids)
    regions = count_regions(idpoints)
    heatmap_points(pointids, "All Fragility Points: " + title)
    heatmap_points(pps, "Pareto Fragility Points: " + title)


if __name__ == "__main__":
    '''
    pointids, idpoints = get_points("./data/control/")
    pps = pareto(pointids)
    regions = count_regions(idpoints)
    heatmap_points(pointids, "All Points: Control")
    heatmap_points(pps, "Pareto Points: Control")
    compensation(pps, regions, "./Participant ID and Email (Responses).xlsx", "control_money.xlsx")
    fragility("./data/control/", "Control")
    '''
    '''
    pointids, idpoints = get_points("./data/margin/")
    pps = pareto(pointids)
    regions = count_regions(idpoints)
    heatmap_points(pointids, "All Points: Margin")
    heatmap_points(pps, "Pareto Points: Margin")
    compensation(pps, regions, "./Participant ID and Email (Responses).xlsx", "margin_money.xlsx")
    fragility("./data/margin/", "Margin")
    '''
    '''
    pointids, idpoints = get_points("./data/robust_performance/")
    pps = pareto(pointids)
    regions = count_regions(idpoints)
    heatmap_points(pointids, "All Points: Robust Performance")
    heatmap_points(pps, "Pareto Points: Robust Performance")
    compensation(pps, regions, "./Participant ID and Email (Responses).xlsx", "robperf_money.xlsx")
    fragility("./data/robust_performance/", "Robust Performance")
    '''
    '''
    pointids, idpoints = get_points("./data/robust_gamma/")
    pps = pareto(pointids)
    regions = count_regions(idpoints)
    heatmap_points(pointids, "All Points: Robust Gamma")
    heatmap_points(pps, "Pareto Points: Robust Gamma")
    compensation(pps, regions, "./Participant ID and Email (Responses).xlsx", "robgamma_money.xlsx")
    fragility("./data/robust_gamma/", "Robust Gamma")
    '''
    