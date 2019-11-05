
from __future__ import print_function
from gpkit import Model, Variable, SignomialsEnabled, VarKey, units
import numpy as np

Var = Variable


class SimPleAC(Model):
    def setup(self):
        # Env. constants
        g = Var("g", 9.81, "m/s^2", "gravitational acceleration")
        mu = Var("mu", 1.775e-5, "kg/m/s", "viscosity of air", pr=4.)
        rho = Var("rho", 1.23, "kg/m^3", "density of air", pr=5.)
        rho_f = Var("rho_f", 817, "kg/m^3", "density of fuel")

        # Non-dimensional constants
        C_Lmax = Var("C_Lmax", 1.6, "-", "max CL with flaps down", pr=5.)
        e = Var("e", 0.92, "-", "Oswald efficiency factor", pr=3.)
        k = Var("k", 1.17, "-", "form factor", pr=10.)
        N_ult = Var("N_ult", 3.3, "-", "ultimate load factor", pr=15.)
        S_wetratio = Var("S_wetratio", 2.075, "-", "wetted area ratio", pr=3.)
        tau = Var("tau", 0.12, "-", "airfoil thickness to chord ratio", pr=10.)
        W_W_coeff1 = Var("W_W_coeff1", 2e-5, "1/m",
                         "wing weight coefficent 1", pr=30.)  # orig 12e-5
        W_W_coeff2 = Var("W_W_coeff2", 60., "Pa",
                         "wing weight coefficent 2", pr=10.)

        # Dimensional constants
        Range = Var("Range", 3000, "km", "aircraft range")
        TSFC = Var("TSFC", 0.6, "1/hr", "thrust specific fuel consumption")
        V_min = Var("V_{min}", 25, "m/s", "takeoff speed", pr=20.)
        W_0 = Var("W_0", 6250, "N", "aircraft weight excluding wing", pr=20.)

        # Free Vs
        LoD = Var('L/D', '-', 'lift-to-drag ratio')
        D = Var("D", "N", "total drag force")
        V = Var("V", "m/s", "cruising speed")
        W = Var("W", "N", "total aircraft weight")
        Re = Var("Re", "-", "Reynold's number")
        CDA0 = Var("(CDA0)", "m^2", "fuselage drag area")  # 0.035 originally
        C_D = Var("C_D", "-", "drag coefficient")
        C_L = Var("C_L", "-", "lift coefficient of wing")
        C_f = Var("C_f", "-", "skin friction coefficient")
        W_f = Var("W_f", "N", "fuel weight")
        V_f = Var("V_f", "m^3", "fuel volume")
        V_f_avail = Var("V_{f_{avail}}", "m^3", "fuel volume available")
        T_flight = Var("T_{flight}", "hr", "flight time")

        # Free variables (fixed for performance eval.)
        A = Var("A", "-", "aspect ratio", fix=True)
        S = Var("S", "m^2", "total wing area", fix=True)
        W_w = Var("W_w", "N", "wing weight")  # , fix=True)
        W_w_strc = Var('W_w_strc', 'N', 'wing structural weight')  # fix=True)
        W_w_surf = Var('W_w_surf', 'N', 'wing skin weight')  # fix=True)
        V_f_wing = Var("V_f_wing", 'm^3', 'fuel volume in the wing')#, fix=True)
        V_f_fuse = Var('V_f_fuse', 'm^3', 'fuel volume in fuselage')#, fix=True)

        # margins
        m_ww = Var("m_ww", 1, "-", "wing weight margin", margin=True)
        m_tsfc = Var("m_tsfc", 1, "-", "fuel efficiency margin", margin=True)
        m_vmin = Var("m_vmin", 1, "-", "takeoff speed margin", margin=True)
        m_range = Var("m_range", 1, "-", "range margin", margin=True)
        constraints = []

        # Weight and lift model
        constraints += [
            W >= W_0 + W_w + W_f,
            W_0 + W_w + 0.5 * W_f <= 0.5 * rho * S * C_L * V ** 2,
            W <= 0.5 * rho * S * C_Lmax * (V_min/m_vmin) ** 2,
            T_flight >= (Range*m_range) / V,
            LoD == C_L/C_D
            ]

        # Thrust and drag model
        C_D_fuse = CDA0 / S
        C_D_wpar = k * C_f * S_wetratio
        C_D_ind = C_L ** 2 / (np.pi * A * e)
        constraints += [
            W_f >= (TSFC/m_tsfc) * T_flight * D,
            D >= 0.5 * rho * S * C_D * V ** 2,
            C_D >= C_D_fuse + C_D_wpar + C_D_ind,
            V_f_fuse <= 10*units('m')*CDA0,
            Re <= (rho / mu) * V * (S / A) ** 0.5,
            C_f >= 0.074 / Re ** 0.2
            ]

        # Fuel volume model
        with SignomialsEnabled():
            constraints += [
                V_f == W_f / g / rho_f,
                # linear with b and tau, quadratic with chord
                V_f_wing**2 <= 0.0009*S**3/A*tau**2,
                V_f_avail <= V_f_wing + V_f_fuse,  # [SP]
                V_f_avail >= V_f
                ]

        # Wing weight model
        constraints += [
            W_w_surf >= W_W_coeff2 * S,
            W_w_strc**2 >= (W_W_coeff1**2 / tau**2
                            * (N_ult**2 * A**3
                               * ((W_0+V_f_fuse*g*rho_f) * W * S))),
            W_w/m_ww >= W_w_surf + W_w_strc
            ]

        self.cost = W_f

        return constraints


if __name__ == "__main__":
    m = SimPleAC()
    sol = m.localsolve(verbosity=2)
    print(sol.table())
