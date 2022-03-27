import pandas as pd
import numpy as np
import pybamm
import matplotlib.pyplot as plt


def my_current(t):
    """current profile"""
    # return pybamm.sin(2 * np.pi * t / 60)
    return 10.0


drive_cycle = pd.read_csv("tutorials/input/UDDS.csv",
                          comment="#", header=None).to_numpy()

"""models and parameters"""
models = [
    pybamm.lithium_ion.SPM(),
    # pybamm.lithium_ion.SPMe(),
    # pybamm.lithium_ion.DFN(),
]
chem = pybamm.parameter_sets.Chen2020
params = pybamm.ParameterValues(chemistry=chem)

"""solvers"""
sol = pybamm.CasadiSolver(atol=1e-9, rtol=1e-9, mode='safe')
# sol = pybamm.JaxSolver(method="RK45", atol=1e-9, rtol=1e-9)

"""simulate cell"""
sims = []
for model in models:
    """create interpolant"""
    timescale = params.evaluate(model.timescale)
    timeInterpolant = np.linspace(
        0, drive_cycle[-1, 0]*100, np.size(drive_cycle[:, 0])*100)
    currentInterpolant = np.tile(drive_cycle[:, 1], 100)
    plt.plot(timeInterpolant, currentInterpolant)
    plt.show()
    current_interpolant = pybamm.Interpolant(
        timeInterpolant, currentInterpolant, timescale * pybamm.t)

    params['Current function [A]'] = current_interpolant
    # params['Current function [A]'] = my_current
    # params['Lower voltage cut-off [V]'] = 3.0
    # model.events = []
    # model.convert_to_format = "jax"

    sim = pybamm.Simulation(model, parameter_values=params, solver=sol)
    # t_eval = np.arange(0, 3600, 0.1)
    # sim.solve([0, 3600])
    # sim.solve(t_eval=t_eval)
    sim.solve()
    sims.append(sim)

"""plot results"""
output_variables = [
    "Electrolyte concentration [mol.m-3]",
    "Terminal voltage [V]",
    "Positive electrode potential [V]",
    "Negative electrode potential [V]",
]
# sim.plot(output_variables=output_variables)
pybamm.dynamic_plot(sims)
