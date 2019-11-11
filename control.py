
# FILL OUT THESE #

wing_length = 16  # meters
wing_area = 23  # square meters
fuel_volume_available = 0.6  # cubic meters
flight_speed = 50  # meters per second

# EXPERIMENT PARTICIPANTS: DON'T MODIFY BELOW THIS!!! #


from simpleac import SimPleAC
from monte_carlo import monte_carlo_results

m = SimPleAC()
m.substitutions.update({
  "S": wing_area,
  "A": wing_length**2/float(wing_area),
  "V_{f_{avail}}": fuel_volume_available,
  "V": flight_speed
})

monte_carlo_results(m)
