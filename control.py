
# FILL OUT THESE #

wing_length = 16  # meters
wing_area = 23  # square meters
fuel_volume_available = 0.6  # cubic meters
flight_speed = 50  # meters per second

# EXPERIMENT PARTICIPANTS: DON'T MODIFY BELOW THIS!!! #



import numpy as np
from simpleac import SimPleAC

m = SimPleAC()
m.substitutions.update({
  "S": wing_area,
  "A": wing_length**2/float(wing_area),
  "V_{f_{avail}}": fuel_volume_available,
  "V": flight_speed
})


print("\n=========== NEW DESIGN")
try:
    sol = m.localsolve(verbosity=0)
    print("fuel consumption: %i lbs" % sol("W_f").to("lbf").magnitude)
except Exception:
    print "INFEASIBLE"
else:
    N = 29
    failures = 0
    for var in m.varkeys:
        if var.fixed:
            m.substitutions[var] = sol["variables"][var]
    for val in np.linspace(1e-5, 4e-5, N):
        m.substitutions["W_W_coeff1"] = val
        try:
            m.localsolve(verbosity=0, x0=sol["variables"])
        except Exception:
            failures += 1
    print "    failure rate: % 2.1f%% " % (100*failures/float(N))
