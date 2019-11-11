
# FILL OUT THESE #

gamma = 0.057
wing_weight_pr = 10
tsfc_pr = 10.
v_min_pr = 20.
range_pr = 10.

# EXPERIMENT PARTICIPANTS: DON'T MODIFY BELOW THIS!!! #


from simpleac import SimPleAC
from monte_carlo import monte_carlo_results
from robust.robust import RobustModel

m = SimPleAC(wing_weight_pr, tsfc_pr, v_min_pr, range_pr)
nominal_sol = m.localsolve(verbosity=0)

rm = RobustModel(m, "elliptical", gamma=gamma, twoTerm=True,
                 boyd=False, simpleModel=False,
                 nominalsolve=nominal_sol)

rm_sol = rm.robustsolve(verbosity=0,
                        minNumOfLinearSections=3,
                        maxNumOfLinearSections=99,
                        linearizationTolerance=1e-4)

monte_carlo_results(m, sol=rm_sol)
