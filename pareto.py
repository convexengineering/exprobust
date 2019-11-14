import os
import pickle
import plotly.graph_objects as go
from monte_carlo import monte_carlo_results
from simpleac import SimPleAC

# pareto_points = [((perf, fail), [id#, ...]), ...]
def pareto(folder_name, m=SimPleAC()):
    pareto_points = []
    for subject in sorted(os.listdir(folder_name)):
        subj_path = folder_name + subject
        points = sorted([x for x in os.listdir(subj_path)
                         if not x.endswith(".txt")], key = int)
        for point in points:
            im_pareto = True
            im_not_pareto = []
            same = None
            print(subj_path + "/" + point)
            f = open(subj_path + "/" + point, "rb")
            sol = pickle.load(f)
            perf, fail = monte_carlo_results(m, sol=sol)
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
    return pareto_points

if __name__ == "__main__":
    print(pareto("./data/control/"))
    print(pareto("./data/margin/"))
    
    '''    
    TODO: Robust paretos
    from robust.robust import RobustModel
    from gpkit import Variable, units

    print(pareto("./data/robust_performance/", m=))
    
    gamma = Variable('Gamma', '-', 'Uncertainty bound')
    m = SimPleAC(wing_weight_pr.value, tsfc_pr.value, v_min_pr.value, range_pr.value)
    nominal_sol = m.localsolve(verbosity=0)

    m.append(m["W_f"] <= performance.value*units.lbf)
    m.append(gamma <= 1e30)
    m.cost = 1/gamma

    rm = RobustModel(m, "box", gamma=gamma,
                     twoTerm=False, boyd=False, simpleModel=True,
                     nominalsolve=nominal_sol)

    print(pareto("./data/robust_gamma/", m=))

