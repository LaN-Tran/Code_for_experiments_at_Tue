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

number_of_sweeps_vds = 5
    # = `len(vd_sweep)`, file `./fixed_vds_sweep_vgs_measure_ids_v2.py` 
len_data_per_sweep_vds = 726
    # = `(len(list_fvotl) + len(list_bvotl))*number_of_sweeps`, file `./fixed_vds_sweep_vgs_measure_ids_v2.py`

data = pd.read_csv("C:/Users/20245580/LabCode/Codes_For_Experiments/exp_data/20260518\\oect_profiling_transfer_curve.csv")

t = data['time'].to_numpy()
id = data['i_channel'].to_numpy()
vd= data['v_drain'].to_numpy()
ig = data['i_gate'].to_numpy()
vg = data['v_gate'].to_numpy()

for iter_sweep in range(0,number_of_sweeps_vds):
    # because of ids is measured first -> vgs is sourced after that,
    # this is shown by looking at the timestamp of gate voltage and drain current,
    # in `oect_profiling_transfer_curve.csv`
    vgs = vg[iter_sweep*len_data_per_sweep_vds : ((iter_sweep+1)*len_data_per_sweep_vds-1)]
        # the array excludes the last index `(iter_sweep+1)*len_data_per_sweep`
    ids = id[(iter_sweep*len_data_per_sweep_vds+1) : (iter_sweep+1)*len_data_per_sweep_vds]
    vds = vd[iter_sweep*len_data_per_sweep_vds]
    plt.plot(vgs, ids, label=f'$V_{{ds}} = {vds}V$')

# 3. Formatting
plt.xlabel('$V_{gs}$ (V)')
plt.ylabel('$I_{ds}$ (A)')
plt.title('OECT $I_{ds}$-$V_{gs}$ Characteristics')
plt.legend()
plt.grid(True)
plt.show()
