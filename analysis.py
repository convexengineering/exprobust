import os
import pickle
import pandas as pd
import numpy as np
import scipy.stats as stats
import itertools
# import plotly.graph_objects as go
from monte_carlo import monte_carlo_results
from simpleac import SimPleAC

analysis_plot_dir = "./analysis/"
folder_names = ["./data/control/", "./data/margin/", "./data/robust_performance/", "./data/robust_gamma/"]
conditions = ["Control", "Margin", "Robust Performance", "Robust Gamma"]

def determine_settings(condition, folder_name, point_end="_point.txt"):
    ids = sorted(os.listdir(folder_name))
    for subject in ids:
        subj_path = folder_name + subject
        subj_points = sorted([x for x in os.listdir(subj_path)
                         if not x.endswith(".txt")], key = int)
        for subj_point in subj_points:
            point_path = subj_path + "/" + subj_point
            if os.path.isfile(point_path + point_end):
                with open(point_path + point_end, "r") as f:
                    all_lines = f.readlines()
                if all_lines[0] == "unknown\n":
                    settings = []
                    with open(point_path, "rb") as f:
                        sol = pickle.load(f)
                    if condition == conditions[0]:
                        settings.append((sol("A").magnitude*sol("S").magnitude)**0.5)
                        settings.append(sol("S").magnitude)
                        settings.append(sol("V_{f_{avail}}").magnitude)
                        settings.append(sol("C_L").magnitude)
                        print(subj_point)
                        print(settings)
                        with open(point_path + point_end, "w") as f:
                            f.write(str(settings)+"\n")
                            for line in all_lines[1:]:
                                f.write(line)
                    elif condition == conditions[1]:
                        settings.append(sol("m_ww").magnitude)
                        settings.append(sol("m_tsfc").magnitude)
                        settings.append(sol("m_vmin").magnitude)
                        settings.append(sol("m_range").magnitude)
                        print(subj_point)
                        print(settings)
                        with open(point_path + point_end, "w") as f:
                            f.write(str(settings)+"\n")
                            for line in all_lines[1:]:
                                f.write(line)


def save_point(point_path, point_end="_point.txt", model_gen=SimPleAC, seed=246, settings="unknown"):
    with open(point_path, "rb") as f:
        sol = pickle.load(f)
        perf, fail = monte_carlo_results(model_gen(), sol=sol, quiet=True, seed=seed)
    with open(point_path + point_end, "w") as f:
        f.write(str(settings) + "\n")
        f.write(str(perf)+", "+str(fail))
    return perf, fail


def get_points(folder_name, point_end="_point.txt", model_gen=SimPleAC, seed=246):
    pointids = {}
    idpoints = {}
    pointnum = {}
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
                    pointnum[(perf, fail, subject)] = subj_point
            else:
                pointids[(perf, fail)] = [subject]
                pointnum[(perf, fail, subject)] = subj_point
            idpoints[subject].append((perf,fail))
    return pointids, idpoints, pointnum


def corrected_points(folder_name, point_end="_point.txt", model_gen=SimPleAC, seed=246):
    pointids = {}
    idpoints = {}
    pointnum = {}
    skipped = {}
    ids = sorted(os.listdir(folder_name))
    for subject in ids:
        idpoints[subject] = []
        skipped[subject] = []
        subj_path = folder_name + subject
        subj_points = sorted([x for x in os.listdir(subj_path)
                         if not x.endswith(".txt")], key = int)
        for subj_point in subj_points:
            perf = None
            point_path = subj_path + "/" + subj_point
            if os.path.isfile(point_path + point_end):
                with open(point_path + point_end, "r") as f:
                    all_lines = f.readlines()
                    pf_line = all_lines[1]
                    _, fail = [float(x) for x in pf_line.split(", ")]
                    if len(all_lines) >= 3:
                        perf = "SKIP" if "SKIP" in all_lines[2] else float(all_lines[2])
            else:
                _, fail = save_point(point_path, point_end=point_end, model_gen=model_gen, seed=seed)
            if perf is None:
                with open(point_path, "rb") as f:
                    sol = pickle.load(f)
                    nominal = SimPleAC(substitutions={k: sol(k) for k in ["S", "A", "V_{f_{avail}}", "C_L"]})
                    try:
                        nomsol = nominal.localsolve(verbosity=0)
                        perf = nomsol("W_f").to("lbf").magnitude
                    except Exception:
                        perf = "SKIP"
                with open(point_path + point_end, "a") as f:
                    f.write("\n" + str(perf))
            if perf != "SKIP" and perf != "SKIP\n":
                if (perf, fail) in pointids:
                    if subject not in pointids[(perf, fail)]:
                        pointids[(perf, fail)].append(subject)
                        pointnum[(perf, fail, subject)] = subj_point
                else:
                    pointids[(perf, fail)] = [subject]
                    pointnum[(perf, fail, subject)] = subj_point
                idpoints[subject].append((perf,fail))
            else:
                skipped[subject].append(subj_point)

    return pointids, idpoints, pointnum, skipped


def count_regions(idpoints):
    regions = {}
    numregions = {}
    for idnum in idpoints:
        regions[idnum] = 0
        in_green = 0
        in_yellow = 0
        in_blue = 0
        for point in idpoints[idnum]:
            perf, fail = point
            if (perf <= 1200 and fail <= 30):
                in_green += 1
            elif (perf <= 2000 and fail <= 10):
                in_yellow += 1
            elif (perf <= 1100):
                in_blue += 1
        if in_green>0:
            regions[idnum] +=1
        if in_yellow>0:
            regions[idnum] +=1
        if in_blue>0:
            regions[idnum] +=1
        numregions[idnum] = (in_green, in_yellow, in_blue)
    return regions, numregions


def pareto(pointids):
    pareto_points = {}
    for point in pointids:
        perf, fail = point
        if (perf < 900 or perf > 2000):
            continue
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


def plot_points(points, title):
    x, y = list(zip(*points.keys()))
    colors = [len(ids) for ids in points.values()]
    fig = go.Figure(
        data=[go.Scatter(
            x=x,
            y=y,
            marker=dict(
                size=6,
                color=colors,
                cmin=0,
                cmax=8,
                opacity=0.6,
                colorbar=dict(
                    title="",
                    outlinewidth=0,
                    tickwidth=0,
                    tickcolor='white'),
                colorscale="magma"),
            mode="markers")],
        layout_title_text=title)
    fig.update_layout(
        autosize=False,
        width=800,
        height=600,
        yaxis=go.layout.YAxis(
            title_text="Failure Rate",
            range=[0,100],
            tickmode='array',
            tickvals=[0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100],
            ticktext=["0%", "10%", "20%", "30%", "40%", "50%", "60%", "70%", "80%", "90%", "100%"]
        ),
        xaxis=go.layout.XAxis(
            title_text="Fuel Consumed (lbs)",
            range=[900,2000]
        )
    )
    fig.add_shape(
        go.layout.Shape(
            type="rect",
            x0=1200,
            y0=0,
            x1=2000,
            y1=10,
            fillcolor="rgba(240,255,220,0.4)",
            line=dict(
                color="white",
                width=1,
            ),
    ))
    fig.add_shape(
        go.layout.Shape(
            type="rect",
            x0=900,
            y0=30,
            x1=1100,
            y1=100,
            fillcolor="rgba(220,255,240,0.4)",
            line=dict(
                color="white",
                width=1,
            ),
    ))
    fig.add_shape(
        go.layout.Shape(
            type="rect",
            x0=900,
            y0=0,
            x1=1200,
            y1=30,
            fillcolor="rgba(200,255,200,0.4)",
            line=dict(
                color="white",
                width=1,
            ),
    ))
    fig.update_shapes(dict(xref='x', yref='y'))
    fig.show()
    if not os.path.exists(analysis_plot_dir):
        os.mkdir(analysis_plot_dir)
    fig.write_image(analysis_plot_dir+title+".png")


def heatmap_points(points, title):
    hmap = np.zeros((51, 112)) +.0001
    for perf, fail in points:
        i_col = min(max(int((perf-900)/10)+1, 0), 111)
        i_row = int(fail/2)
        hmap[i_row, i_col] += 1
    hmap = np.log(hmap)
    ticks = np.round(np.logspace(np.log10(5),np.log10(80),5))
    x = [0] + list(np.linspace(900, 2000, 111)) + [6000]
    y = list(np.linspace(0, 100, 51))
    fig = go.Figure(
        data=[go.Heatmap(
            x=x,
            y=y,
            z=hmap,
            type = 'heatmap',
            zmin=-1,
            zmax=np.log(80),
            colorbar=dict(
                tickvals=np.log(ticks),
                ticktext=ticks),
            colorscale="magma")],
        layout_title_text=title)
    fig.update_layout(
        autosize=False,
        width=800,
        height=600,
        yaxis=go.layout.YAxis(
            title_text="Failure Rate",
            range=[0,100],
            tickmode = 'array',
            tickvals = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100],
            ticktext = ["0%", "10%", "20%", "30%", "40%", "50%", "60%", "70%", "80%", "90%", "100%"]
        ),
        xaxis=go.layout.XAxis(
            title_text="Fuel Consumed (lbs)",
            range=[900,2000]
        )
    )
    fig.show()
    if not os.path.exists(analysis_plot_dir):
        os.mkdir(analysis_plot_dir)
    fig.write_image(analysis_plot_dir+title+".png")


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
            comp[idnum] += all_3
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
    pointids, _, pointnum = get_points(folder_name, model_gen=model_gen)
    fragpointids, _, _ = get_points(folder_name, point_end, model_gen, seed)
    pps = pareto(pointids)
    fragpps = {}
    for pp in pps:
        for subject in pps[pp]:
            subj_point = pointnum[(pp, subject)]
            point_path = folder_name + subject + "/" + subj_point
            with open(point_path + point_end, "r") as f:
                pf_line = f.readlines()[1]
                perf, fail = [float(x) for x in pf_line.split(", ")]
            if (perf, fail) in fragpps:
                if subject not in fragpps[(perf, fail)]:
                    fragpps[(perf, fail)].append(subject)
            else:
                fragpps[(perf, fail)] = [subject]

    pps = pareto(pointids)
    plot_points(fragpointids, "All Fragility Points-" + title + " (seed %i)" %seed)
    plot_points(fragpps, "Pareto Fragility Points-" + title + " (seed %i)" %seed)
    heatmap_points(fragpointids, "Fragility Heatmap-" + title + " (seed %i)" %seed)


def all_analysis(folder_name, condition):
    #pointids, idpoints, _ = get_points(folder_name)
    pointids, idpoints, _, _ = corrected_points(folder_name)
    pps = pareto(pointids)
    regions, _ = count_regions(idpoints)
    plot_points(pointids, "All Points-" + condition)
    plot_points(pps, "Pareto Points-" + condition)
    heatmap_points(pointids, "Heatmap-" + condition)
    #compensation(pps, regions, "./Participant ID and Email (Responses).xlsx",
    #             analysis_plot_dir + condition + "_Money.xlsx")

    #fragility(folder_name, condition)
    #fragility(folder_name, condition, seed=839)


def summary_stats():
    numpoints = {condition: [] for condition in conditions}
    numgreen = {condition: [] for condition in conditions}
    numyellow = {condition: [] for condition in conditions}
    numblue = {condition: [] for condition in conditions}
    numout = {condition: [] for condition in conditions}
    norm_numgreen = {condition: [] for condition in conditions}
    norm_numyellow = {condition: [] for condition in conditions}
    norm_numblue = {condition: [] for condition in conditions}
    norm_numout = {condition: [] for condition in conditions}
    endtimes = {condition: [] for condition in conditions}
    timesgreen = {condition: [] for condition in conditions}
    timesyellow = {condition: [] for condition in conditions}
    timesblue = {condition: [] for condition in conditions}
    for folder_name, condition in zip(folder_names, conditions):
        _, idpoints, pointnum, skipped = corrected_points(folder_name)
        numpoints[condition] = [len(idpoints[idnum]) for idnum in idpoints]
        _, numregions = count_regions(idpoints)
        numgreen[condition], numyellow[condition], numblue[condition] = list(zip(*numregions.values()))
        numout[condition] = np.subtract(np.subtract(np.subtract(numpoints[condition], numgreen[condition]), numyellow[condition]), numblue[condition])
        norm_numgreen[condition] = np.divide(numgreen[condition], numpoints[condition])
        norm_numyellow[condition] = np.divide(numyellow[condition], numpoints[condition])
        norm_numblue[condition] = np.divide(numblue[condition], numpoints[condition])
        norm_numout[condition] = np.divide(numout[condition], numpoints[condition])
        times = {idnum: [] for idnum in idpoints}
        timegreen = {idnum: None for idnum in idpoints}
        timeyellow = {idnum: None for idnum in idpoints}
        timeblue = {idnum: None for idnum in idpoints}
        for point in pointnum:
            times[point[2]].append(int(pointnum[point]))
            if (timegreen[point[2]] is None and (point[0] <= 1200 and point[1] <= 30)):
                timegreen[point[2]] = int(pointnum[point])
            elif (timeyellow[point[2]] is None and ((point[0] <= 2000 and point[0] > 1200) and point[1] <= 10)):
                timeyellow[point[2]] = int(pointnum[point])
            elif (timeblue[point[2]] is None and (point[0] <= 1100 and point[1] > 30)):
                timeblue[point[2]] = int(pointnum[point])
        timesgreen[condition] = [timegreen[idnum] - min(times[idnum]) for idnum in times if timegreen[idnum] is not None]
        timesyellow[condition] = [timeyellow[idnum] - min(times[idnum]) for idnum in times if timeyellow[idnum] is not None]
        timesblue[condition] = [timeblue[idnum] - min(times[idnum]) for idnum in times if timeblue[idnum] is not None]
        endtimes[condition] = [max(times[idnum]) - min(times[idnum]) for idnum in times]

        #print(condition + " Time to Yellow")
        #print(timesyellow[condition])
        #print("Average: %f" %np.mean(timesyellow[condition]))
        #print("StDev: %f" %np.std(timesyellow[condition]))
        print(condition + " Skipped")
        print(skipped)
        '''
        print(condition + " Norm Out")
        print(norm_numout[condition].tolist())
        print("Average: %f" %np.mean(norm_numout[condition]))
        print("StDev: %f" %np.std(norm_numout[condition]))
        '''

    print("T-Tests")
    for condition1, condition2 in itertools.combinations(conditions, 2):
        _, pval = stats.ttest_ind(timesyellow[condition1], timesyellow[condition2], equal_var=False, nan_policy='raise')
        print("%s, %s p-value: %f" %(condition1, condition2, pval))

    '''
    fig = go.Figure()
    for condition in all_numpoints:
        fig.add_trace(go.Violin(y=all_numpoints[condition],
                            name=condition,
                            points='all',
                            box_visible=True,
                            meanline_visible=True))
    fig.update_layout(
        autosize=False,
        width=800,
        height=600,
        showlegend=False,
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=go.layout.XAxis(
            title_text="Condition",
        ),
        yaxis=go.layout.YAxis(
            title_text="Number of Points",
            range=[0,300],
            ticks="outside",
            gridcolor='rgba(0,0,0,.1)'
        )
    )
    fig.show()
    '''


if __name__ == "__main__":
    # for folder_name, condition in zip(folder_names, conditions):
    #     all_analysis(folder_name, condition)
    summary_stats()
