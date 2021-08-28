import pybamm
import matplotlib.pyplot as plt

chemistry = pybamm.parameter_sets.Chen2020
parameter_values = pybamm.ParameterValues(chemistry=chemistry)
graphite_ocv = parameter_values['Negative electrode OCP [V]'][1]
nmc_ocv = parameter_values['Positive electrode OCP [V]'][1]


"""plot results"""
plt.figure(1)
ax1 = plt.subplot(111)
ax1.plot(graphite_ocv[:, 0], graphite_ocv[:, 1])
ax1.grid(True)
ax1.set_title('Graphite OCP')
ax1.set_xlabel('SOC')
ax1.set_ylabel('Potential [V]')

plt.figure(2)
ax2 = plt.subplot(111)
ax2.plot(nmc_ocv[:, 0], nmc_ocv[:, 1])
ax2.grid(True)
ax2.set_title('NMC OCP')
ax2.set_xlabel('SOC')
ax2.set_ylabel('Potential [V]')
plt.show()