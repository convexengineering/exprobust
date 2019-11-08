import numpy as np


def monte_carlo_results(m, progress, out):
    try:
        sol = m.localsolve(verbosity=0)
        with out:
            print("fuel consumption: %i lbs" % sol("W_f").to("lbf").magnitude)
    except Exception:
        return (None,None)
    else:
        N = 29
        min_val = 1e-5
        max_val = 4e-5
        failures = 0
        for var in m.varkeys:
            if var.fix:
                m.substitutions[var] = sol["variables"][var]
            if var.margin:
                m.substitutions[var] = 1
        for val in np.linspace(min_val, max_val, N):
            m.substitutions["W_W_coeff1"] = val
            try:
                m.localsolve(verbosity=0, x0=sol["variables"])
            except Exception:
                failures += 1
            progress.value = (val-min_val)/(max_val-min_val)
        with out:
            print("    failure rate: % 2.1f%% " % (100*failures/float(N)))
        return (sol("W_f").to("lbf").magnitude, 100*failures/float(N))

    