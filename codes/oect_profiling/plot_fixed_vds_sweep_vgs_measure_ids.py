"""
    Automation Keithley 2602B
    OECT PROFILING -TRANSFER MEASUREMENT
    sweep vgs, measure ids, fixed vds
    Author:  Tran Le Phuong Lan.
    Created:  2026-05-14

    Requires:                       
       Python 2.7, 3
       pyvisa
       ?? pyusb
    Reference:
        [1] https://github.com/LaN-Tran/Automate_Lab_Instrument/tree/main/20250905

"""

import matplotlib.pyplot as plt
import pandas as pd
# from scipy import signal
import numpy as np

number_of_sweeps = 3
    # = `len(vg_sweep)`, file `./fixed_vgs_sweep_vds_measure_ids.py` 
len_data_per_sweep = 202
    # = `llen(list_fvotl) + len(list_bvotl)`, file `./fixed_vgs_sweep_vds_measure_ids.tsp`

data = pd.read_csv("C:/Users/20245580/LabCode/Codes_For_Experiments/exp_data/20260119\\plot_fixed_vds_sweep_vgs_measure_ids.csv")

t = data['time'].to_numpy()
id = data['i_channel'].to_numpy()
vd= data['v_drain'].to_numpy()
ig = data['i_gate'].to_numpy()
vg = data['v_gate'].to_numpy()

for iter_sweep in range(0,number_of_sweeps):
    vgs = vg[iter_sweep*len_data_per_sweep : (iter_sweep+1)*len_data_per_sweep]
        # the array excludes the last index `(iter_sweep+1)*len_data_per_sweep`
    ids = id[iter_sweep*len_data_per_sweep : (iter_sweep+1)*len_data_per_sweep]
    vds = vd[iter_sweep*len_data_per_sweep]
    plt.plot(vgs, ids, label=f'$V_{{gs}} = {vds}V$')

# 3. Formatting
plt.xlabel('$V_{gs}$ (V)')
plt.ylabel('$I_{ds}$ (A)')
plt.title('OECT $I_{ds}$-$V_{gs}$ Characteristics')
plt.legend()
plt.grid(True)
plt.show()
