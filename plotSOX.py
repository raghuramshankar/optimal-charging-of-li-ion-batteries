import numpy as np
import pybamm
import matplotlib.pyplot as plt

pybamm.set_logging_level("NOTICE")
experiment = pybamm.Experiment(
    [
        (
            "Discharge at C/5 for 10 hours or until 2.5V",
            "Rest for 1 hour",
            "Charge at 1 A until 4.2 V",
            "Hold at 4.2 V until 10 mA",
            "Rest for 1 hour",
        ),
    ]
)
model = pybamm.lithium_ion.DFN()
params = pybamm.ParameterValues("Chen2020")

sim = pybamm.Simulation(
    model, experiment=experiment, parameter_values=params, solver=pybamm.CasadiSolver(
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
    "X-averaged positive particle concentration [mol.m-3]",
]

# Plot OCV
# OCV = positive OCP - negative OCP
posOCP = sim.solution["Positive electrode potential [V]"].data[1, :]
negOCP = sim.solution["Negative electrode potential [V]"].data[1, :]
cellOCV = posOCP - negOCP

# Plot cell capacity
disCap = sim.solution["Discharge capacity [A.h]"].data
negCap = sim.solution["Negative electrode capacity [A.h]"].data
posCap = sim.solution["Positive electrode capacity [A.h]"].data
cellCap = min(negCap[0], posCap[0])
print(cellCap)

# Plot SOC
posConcAvg = sim.solution["X-averaged positive particle concentration [mol.m-3]"].data
posConcAvg = [np.mean(posConcAvg[:, i])
              for i in range(np.shape(posConcAvg)[1])]
negConcAvg = sim.solution["X-averaged negative particle concentration [mol.m-3]"].data
negConcAvg = [np.mean(negConcAvg[:, i])
              for i in range(np.shape(negConcAvg)[1])]

posConcMax = params["Maximum concentration in positive electrode [mol.m-3]"]
negConcMax = params["Maximum concentration in negative electrode [mol.m-3]"]

# csavg/csmax
posConc = np.divide(posConcAvg, posConcMax)
negConc = np.divide(negConcAvg, negConcMax)

# x0, x100, y0, y100
posStoicHundred = min(posConc)
negStoicHundred = max(negConc)
posStoicZero = max(posConc)
negStoicZero = min(negConc)

# socpos = (csavgpos/csmaxpos - y0)/(y100 - y0)
cellSOCPos = (posConc - posStoicZero)/(posStoicHundred - posStoicZero)
# socneg = (csavgneg/csmaxneg - x0)/(x100 - x0)
cellSOCNeg = (negConc - negStoicZero)/(negStoicHundred - negStoicZero)

plt.plot(cellSOCNeg)
plt.show()

# sim.solution.save_data("output.csv", output_variables, to_format="csv")
# sim.plot(output_variables=output_variables)

print('Done')
