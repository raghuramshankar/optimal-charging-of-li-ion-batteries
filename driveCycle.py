import pandas as pd
import numpy as np
import pybamm

pybamm.set_logging_level("NOTICE")
driveCycle = pd.read_csv("tutorials/input/UDDS.csv",
                         comment="#", header=None).to_numpy()

"""models and parameters"""
model = pybamm.lithium_ion.SPM()
chem = pybamm.parameter_sets.Chen2020
params = pybamm.ParameterValues(chemistry=chem)

"""solvers"""
sol = pybamm.CasadiSolver("fast with events")

"""simulate cell"""
sims = []
"""create interpolant"""
timescale = params.evaluate(model.timescale)
xInterpolant = np.linspace(
    0, driveCycle[-1, 0]*100, np.size(driveCycle[:, 0])*100)
yInterpolant = np.tile(driveCycle[:, 1], 100)
currentInterpolant = pybamm.Interpolant(
    xInterpolant, yInterpolant, timescale * pybamm.t)

params['Current function [A]'] = currentInterpolant
# params['Lower voltage cut-off [V]'] = 3.0
# model.events = []

sim = pybamm.Simulation(model, parameter_values=params, solver=sol)
sim.solve()
sims.append(sim)

"""plot results"""
output_variables = [
    "Electrolyte concentration [mol.m-3]",
    "Terminal voltage [V]",
    "Current [A]",
    "Positive electrode potential [V]",
    "Negative electrode potential [V]"
]
sim.plot(output_variables=output_variables)
# pybamm.dynamic_plot(sims)
