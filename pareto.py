import os
import pickle
import plotly.graph_objects as go
from monte_carlo import monte_carlo_results
from simpleac import SimPleAC

# pareto_points = [((perf, fail), [id#, ...]), ...]
def pareto_regions(folder_name, model_gen=SimPleAC):
    pareto_points = []
    regions = {}
    for subject in sorted(os.listdir(folder_name)):
        subj_path = folder_name + subject
        points = sorted([x for x in os.listdir(subj_path)
                         if not x.endswith(".txt")], key = int)
        regions[subject] = 0
        in_green = False
        in_blue = False
        in_yellow = False
        
        for point in points:
            im_pareto = True
            im_not_pareto = []
            same = None
            f = open(subj_path + "/" + point, "rb")
            sol = pickle.load(f)
            perf, fail = monte_carlo_results(model_gen(), sol=sol, quiet=True)
            for i, pareto_point in enumerate(pareto_points):
                if (pareto_point[0][0] < perf and pareto_point[0][1] < fail):
                    im_pareto = False
                    break
                elif (pareto_point[0][0] >= perf and pareto_point[0][1] >= fail):
                    if (pareto_point[0][0] == perf and pareto_point[0][1] == fail):
                        same = i
                        break
                    else:
                        im_not_pareto.append(i)
            if same is not None:
                pareto_points[i][1].append(subject)
            else:
                im_not_pareto.reverse()
                for i in im_not_pareto:
                    pareto_points.pop(i)
                if im_pareto:
                    pareto_points.append(((perf, fail), [subject]))

            if (not in_green and (perf <= 1200 and fail <= 30)):
                regions[subject] += 1
                in_green = True
            elif (not in_yellow and (perf <= 2000 and fail <= 10)):
                regions[subject] += 1
                in_yellow = True
            elif (not in_blue and (perf <= 1100)):
                regions[subject] += 1
                in_blue = True

    return pareto_points, regions

#def plot_pareto(pareto_points):


#def compensation(pareto_points, regions, idfile):



if __name__ == "__main__":
    print(pareto_regions("./data/control/"))
    print(pareto_regions("./data/margin/"))
    print(pareto_regions("./data/robust_performance/"))
    print(pareto_regions("./data/robust_gamma/"))
