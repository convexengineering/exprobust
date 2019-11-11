
# FILL OUT THESE #

wing_weight_margin = 1.125
tsfc_margin = 1.
takeoff_speed_margin = 1.
range_margin = 1.

# EXPERIMENT PARTICIPANTS: DON'T MODIFY BELOW THIS!!! #


from simpleac import SimPleAC
from monte_carlo import monte_carlo_results

m = SimPleAC()
m.substitutions.update({
  "m_ww": wing_weight_margin,
  "m_tsfc": tsfc_margin,
  "m_vmin": takeoff_speed_margin,
  "m_range": range_margin
})

monte_carlo_results(m)
