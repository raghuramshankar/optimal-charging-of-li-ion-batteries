import pybamm
import pandas as pd

chem = pybamm.parameter_sets.Chen2020
params = pybamm.ParameterValues(chemistry=chem)

df = pd.DataFrame(params.keys())
df.to_csv('params.csv', index=False)