import pybamm

"""define experiment"""
exp = pybamm.Experiment(
    [
        "Discharge at 1C for 0.5 hours",
        "Discharge at C/20 for 0.5 hours",
        "Charge at 0.5 C for 45 minutes",
        "Discharge at 1 A for 90 seconds",
        # "Charge at 200mA for 45 minutes (1 minute period)",
        "Discharge at 1 W for 0.5 hours",
        "Charge at 200 mW for 45 minutes",
        # "Rest for 10 minutes (5 minute period)",
        # "Hold at 1 V for 20 seconds",
        # "Charge at 1 C until 4.1V",
        # "Hold at 4.1 V until 50 mA",
        # "Hold at 3V until C/50"
    ]
    * 1
)

"""define models"""
options = {"thermal": "x-full"}
models = [pybamm.lithium_ion.DFN(options=options)]

solutions = []

"""simulate the cell"""
for model in models:
    sim = pybamm.Simulation(model=model, experiment=exp)
    sim.solve()
    pybamm.dynamic_plot(sim)
    solutions.append(sim.solution)

# """save solutions"""
# for sol in solutions:
#     sol.save('sim_dfn.pkl')
#     sol.save_data('sim_dfn.csv', ['Current [A]', 'Terminal voltage [V]'], to_format='csv')
