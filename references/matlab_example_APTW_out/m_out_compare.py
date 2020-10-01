import numpy as np
import pandas as pd

df_m_out_m = pd.read_csv('references/matlab_example_APTW_out/M_out.csv')
m_out_m = df_m_out_m.to_numpy()

#df_mz_m = pd.read_csv('references/matlab_example_APTW_out/M_z.csv')
df_mz_m = df_m_out_m.iloc[5].reset_index(drop=True)
mz_m = df_mz_m.to_numpy()

df_mz_py = pd.read_csv('references/matlab_example_APTW_out/Mz_py_v2.csv').transpose().reset_index(drop=True)
mz = df_mz_py.to_numpy()

df_compare = pd.concat([df_mz_m, df_mz_py], axis=1)
df_compare.columns = ['Mz (matlab)', 'Mz (python)']
print(df_compare.head(5))

np.allclose(mz_m, mz, rtol=1e-05, atol=1e-08, equal_nan=False)