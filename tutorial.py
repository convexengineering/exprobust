from __future__ import print_function
from gpkit import Model, Variable, SignomialsEnabled, VarKey, units
import numpy as np

Var = Variable


class Tutorial(Model):
    def setup(self):
        # Free Vs
        C_o = Var("C_o", '-', "cost of plane")
        F_a = Var("F_a", '-', "failure rate")
        # Fixed variables
        S_a = Var("S_a", 60, "-", "total surface area", fix=True)

        # Weight and lift model
        constraints = [
            C_o >= (10*S_a) + (10/S_a),
            F_a >= (1/(S_a**2)) * 10000
            ]

        self.cost = C_o

        return constraints


if __name__ == "__main__":
    m = Tutorial()
    sol = m.localsolve(verbosity=2)
    print(sol.table())
