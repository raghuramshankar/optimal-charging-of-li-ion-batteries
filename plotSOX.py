#
# Constant-current constant-voltage charge
#
import pybamm
import matplotlib.pyplot as plt

pybamm.set_logging_level("NOTICE")
experiment = pybamm.Experiment(
    [
        (
            "Discharge at C/5 for 10 hours or until 3.3 V",
            "Rest for 1 hour",
            "Charge at 1 A until 4.1 V",
            "Hold at 4.1 V until 10 mA",
            "Rest for 1 hour",
        ),
    ]
)
model = pybamm.lithium_ion.DFN()

sim = pybamm.Simulation(
    model, experiment=experiment, solver=pybamm.CasadiSolver(
        "fast with events")
)
sim.solve()

# Plot SOX
# fig, ax = plt.subplots()
# for i in range(3):
#     # Extract sub solutions
#     sol = sim.solution.cycles[i]
#     # Extract variables
#     t = sol["Time [h]"].entries
#     V = sol["Terminal voltage [V]"].entries

#     # Plot
#     ax.plot(t - t[0], V, label="Discharge {}".format(i + 1))
#     ax.set_xlabel("Time [h]")
#     ax.set_ylabel("Voltage [V]")
#     ax.set_xlim([0, 10])
# ax.legend(loc="lower left")

# Show all plots
output_variables = [
    "Current [A]",
    "Terminal voltage [V]",
    "X-averaged negative particle concentration [mol.m-3]",
]

# Plot OCV
# OCV = positive OCP - negative OCP
posOCP = sim.solution["Positive electrode potential [V]"].data[1, :]
negOCP = sim.solution["Negative electrode potential [V]"].data[1, :]
cellOCV = posOCP - negOCP

plt.plot(cellOCV)
plt.show()

# sim.solution.save_data("output.csv", output_variables, to_format="csv")
# sim.plot(output_variables=output_variables)

print('Done')
