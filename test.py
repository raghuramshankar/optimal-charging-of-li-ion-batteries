import pybamm
import pandas as pd
import numpy as np

"""current profile"""
def my_current(t):
    return pybamm.sin(2 * np.pi * t / 60)

# drive_cycle = pd.read_csv("input/UDDS.csv", comment="#", header=None).to_numpy()

"""models and parameters"""
models = [
    # pybamm.lithium_ion.SPM(),
    # pybamm.lithium_ion.SPMe(),
    pybamm.lithium_ion.DFN(),
]
chem = pybamm.parameter_sets.Chen2020
params = pybamm.ParameterValues(chemistry=chem)

"""simulate cell"""
sims = []
for model in models:
    """create interpolant"""
    timescale = params.evaluate(model.timescale)
    # current_interpolant = pybamm.Interpolant(drive_cycle[:, 0], drive_cycle[:, 1], timescale * pybamm.t)
    # params['Current function [A]'] = current_interpolant
    params['Current function [A]'] = my_current

    sim = pybamm.Simulation(model, parameter_values=params)
    t_eval = np.arange(0, 121, 1)
    # sim.solve([0, 3600])
    sim.solve(t_eval=t_eval)
    # sim.solve()
    sims.append(sim)

"""plot results"""
output_variables = ["Electrolyte concentration [mol.m-3]", "Terminal voltage [V]", 'Positive electrode potential [V]', 'Negative electrode potential [V]']
# sim.plot(output_variables=output_variables)
pybamm.dynamic_plot(sims)