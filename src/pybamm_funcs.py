# %%
import pybamm


def get_terminal_voltage(dt, N, current, init_soc):
    """
    Predicts the terminal voltage of the cell using an equivalent circuit model over the time horizon
    """
    model = pybamm.equivalent_circuit.Thevenin()
    params = model.default_parameter_values
    params["Initial SoC"] = init_soc
    params["Current function [A]"] = current
    sol = pybamm.CasadiSolver(mode="fast")
    sim = pybamm.Simulation(model, parameter_values=params, solver=sol)
    sim.solve(t_eval=[0, dt * N])
    sim.plot()


if __name__ == "__main__":
    pybamm.set_logging_level("NOTICE")
    current = 100
    dt = 0.01
    N = 360000 / (dt * current)
    init_soc = 1.0
    get_terminal_voltage(dt, N, current, init_soc)
