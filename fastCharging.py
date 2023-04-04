# %%
import matplotlib.pyplot as plt
import polars as pl
import pybamm
import numpy as np
from scipy.optimize import minimize

pybamm.set_logging_level("NOTICE")

if '__ipython__':
    %matplotlib widget
    %load_ext autoreload
    %autoreload 2


class fastCharging:
    def __init__(self):
        options = {"thermal": "lumped"}
        self.model = pybamm.lithium_ion.SPMe(options)
        self.params = pybamm.ParameterValues("Chen2020")
        self.capacity = self.params["Nominal cell capacity [A.h]"]
        self.output_variables = [
            "Current [A]",
            "Terminal voltage [V]",
            "Discharge capacity [A.h]",
            "Ambient temperature [C]",
            "Volume-averaged cell temperature [C]",
            "X-averaged negative electrode reaction overpotential",
        ]
        self.solver = pybamm.CasadiSolver(mode="fast")
        self.anodeDF = pl.DataFrame()
        _, self.ax = plt.subplots(figsize=(12, 6))
        self.maxCRate = -self.capacity * 1
        self.maxTemp = 30

    def currentFnConstantCRate(self, cRate=1):
        return self.capacity * cRate
    
    # def getLumpedInnerTemp(self, solution):
    #     T_amb = self.params["Ambient Temperature [C]"]
    #     Q_vol_av = variables["Volume-averaged total heating"]
    #     cell_surface_area = self.params.a_cooling
    #     cell_volume = self.params.v_cell
    #     total_cooling_coefficient = (
    #         -self.params.h_total
    #         * cell_surface_area
    #         / cell_volume
    #         / (self.params.delta**2)
    #     )
    #     T_vol_av = (self.params.B * Q_vol_av + total_cooling_coefficient * (T_vol_av - T_amb)) / (self.params.C_th * self.params.rho(T_vol_av))

    def costFun(self, x, dt, npts, stepSolution):
        inputs = {"Current function [A]": self.currentFnConstantCRate(cRate=x)}
        stepPredSolution = self.solver.step(
            stepSolution, self.model, dt=dt, npts=npts, inputs=inputs, save=False
        )
        T_vol_av = stepPredSolution["Volume-averaged cell temperature [C]"].entries[-1]
        dischCap = - stepPredSolution["Discharge capacity [A.h]"].entries[-1]

        cost = max(0, (T_vol_av - self.maxTemp)) + (self.capacity - dischCap)
        # cost = max(0, (T_vol_av - self.maxTemp))**2 - dischCap
        # cost =  (self.capacity - dischCap)
        return cost

    def currentFnPredictive(self, stepSolution, dt, npts):
        # setup minimize function arguments
        x0 = self.maxCRate
        bnds = (self.maxCRate, self.maxCRate*0.1)
        optiCurrent = minimize(
            self.costFun,
            x0,
            args=(dt, npts, stepSolution),
            method="SLSQP",
            bounds=(bnds,),
        )

        optiCurrent = optiCurrent.x

        # simulate prediction horizon for npts time steps and dt time
        inputs = {
            "Current function [A]": self.currentFnConstantCRate(cRate=optiCurrent)
        }
        stepPredSolution = self.solver.step(
            stepSolution, self.model, dt=dt, npts=npts, inputs=inputs, save=False
        )

        # plot solution
        self.plotResults(stepPredSolution)
        return optiCurrent

    def plotResults(self, solution):
        plt.plot(
            solution["Time [s]"].entries,
            solution["Volume-averaged cell temperature [C]"].entries,
        )

    def setModelSOC(self, soc, param=None, known_value="cyclable lithium capacity"):
        param = pybamm.LithiumIonParameters()
        x, y = pybamm.lithium_ion.get_initial_stoichiometries(
            soc, self.params, param=param, known_value=known_value
        )
        c_n_max = self.params.evaluate(param.n.prim.c_max)
        c_p_max = self.params.evaluate(param.p.prim.c_max)
        self.params.update(
            {
                "Initial concentration in negative electrode [mol.m-3]": x * c_n_max,
                "Initial concentration in positive electrode [mol.m-3]": y * c_p_max,
            }
        )

    def discModel(self):
        geometry = self.model.default_geometry
        self.params.process_model(self.model)
        self.params.process_geometry(geometry)
        mesh = pybamm.Mesh(
            geometry, self.model.default_submesh_types, self.model.default_var_pts
        )
        disc = pybamm.Discretisation(mesh, self.model.default_spatial_methods)
        disc.process_model(self.model)

    def stepCharge(self):
        # starting settings for simulation
        soc = 0.0
        cRate = -2
        time = 0

        # simulation end time
        # endTime = 3600/cRate
        endTime = 3300

        # sample time in seconds
        sampleTime = 1

        # prediction horizon number of points and time in seconds
        npts = 5
        dt = sampleTime * npts

        # set cell parameters
        self.params["Current function [A]"] = "[input]"
        self.params["Upper voltage cut-off [V]"] = 4.5
        self.params["Lower voltage cut-off [V]"] = 2.0
        self.setModelSOC(soc)
        self.discModel()

        # setup inital model and model settings
        stepSolution = None

        # keep stepping until simulation end time or termination condition is met
        while time < endTime:
            # input current function
            inputs = {
                "Current function [A]": self.currentFnPredictive(stepSolution, dt, npts)
            }

            # apply only the first input and get the first time step
            stepSolution = self.solver.step(
                stepSolution,
                self.model,
                dt=sampleTime,
                npts=npts,
                inputs=inputs,
                save=True,
            )

            time = time + sampleTime
            print("time = ", time)

            # if voltage cut off is reached, stop simulating
            if (
                stepSolution.termination == "event: Minimum voltage"
                or stepSolution.termination == "event: Maximum voltage"
            ):
                break

        stepSolution.plot(output_variables=self.output_variables)


if __name__ == "__main__":
    fastChargingObj = fastCharging()
    fastChargingObj.stepCharge()
