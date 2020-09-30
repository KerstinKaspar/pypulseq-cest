import numpy
import pandas as pd

df_M_out = pd.read_csv('references/matlab_example_APTW_out/M_out.csv')
M_out = df_M_out.to_numpy()

df_Mz = pd.read_csv('references/matlab_example_APTW_out/M_z.csv')
Mz = df_Mz.to_numpy()