from __future__ import print_function
from gpkit import Model, Variable, VarKey, units
import numpy as np

Var = Variable


class Tutorial(Model):
    def setup(self):
        # Free Vs
        C_o = Var("C_o", '-', "cost of plane")
        F_a = Var("F_a", '-', "failure rate")
        # Fixed variables
        S_a = Var("S_a", 2, "-", "total surface area", fix=True)

        # Weight and lift model
        constraints = [
            C_o >= ((10*S_a) + (10/S_a))*50,
            F_a >= (1/(S_a**2)) * 100,
            #C_o >= F_a*100,
            F_a <= 100
            ]

        self.cost = C_o

        return constraints


if __name__ == "__main__":
    m = Tutorial()
    sol = m.solve(verbosity=2)
    print(sol.table())
