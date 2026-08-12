"""
    Automation Keithley 2602B
    OECT PROFILING -OUTPUT MEASUREMENT
    sweep vds, measure ids, fixed gds
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

number_of_sweeps_vgs = 1
    # = `len(vg_sweep)`, file `./fixed_vgs_sweep_vds_measure_ids.py` 
len_data_per_sweep_vgs = 32011
    # = `llen(list_fvotl) + len(list_bvotl)`, file `./fixed_vgs_sweep_vds_measure_ids.tsp`

data = pd.read_csv("C:/Users/20245580/LabCode/Codes_For_Experiments/exp_data/20260518\\oect_profiling_output_curve.csv")

t = data['time'].to_numpy()
id = data['i_channel'].to_numpy()
vd= data['v_drain'].to_numpy()
ig = data['i_gate'].to_numpy()
vg = data['v_gate'].to_numpy()

for iter_sweep in range(0,number_of_sweeps_vgs):
    vds = vd[iter_sweep*len_data_per_sweep_vgs : (iter_sweep+1)*len_data_per_sweep_vgs]
        # the array excludes the last index `(iter_sweep+1)*len_data_per_sweep`
    ids = id[iter_sweep*len_data_per_sweep_vgs : (iter_sweep+1)*len_data_per_sweep_vgs]
    vgs = vg[iter_sweep*len_data_per_sweep_vgs]
    plt.plot(vds, ids, label=f'$V_{{gs}} = {vgs}V$')

# 3. Formatting
plt.xlabel('$V_{ds}$ (V)')
plt.ylabel('$I_{ds}$ (A)')
plt.title('OECT $I_{ds}$-$V_{ds}$ Characteristics')
plt.legend()
plt.grid(True)
plt.show()
