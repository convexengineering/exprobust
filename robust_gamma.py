
# FILL OUT THESE #

performance = 4736  # IN NEWTONS
wing_weight_pr = 10
tsfc_pr = 10.
v_min_pr = 20.
range_pr = 10.

# EXPERIMENT PARTICIPANTS: DON'T MODIFY BELOW THIS!!! #


from simpleac import SimPleAC
from monte_carlo import monte_carlo_results
from robust.robust import RobustModel
from gpkit import Variable

gamma = Variable('Gamma', '-', 'Uncertainty bound')
m = SimPleAC(wing_weight_pr, tsfc_pr, v_min_pr, range_pr)
nominal_sol = m.localsolve(verbosity=0)

m.append(m["W_f"] <= performance*m["W_f"].units)
m.append(gamma <= 1e30)
m.cost = 1/gamma

rm = RobustModel(m, "box", gamma=gamma,
                 twoTerm=False, boyd=False, simpleModel=True,
                 nominalsolve=nominal_sol)

rm_sol = rm.robustsolve(verbosity=0)

m = SimPleAC(wing_weight_pr, tsfc_pr, v_min_pr, range_pr)
monte_carlo_results(m, sol=rm_sol)
