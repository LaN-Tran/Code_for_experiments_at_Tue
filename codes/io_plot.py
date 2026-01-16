"""
 
   Author:  
   Revision:  

   Requires:                       

   Reference:

   - [1] https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.filtfilt.html#scipy.signal.filtfilt

   - [2] https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.ellip.html 
   
"""

import matplotlib.pyplot as plt
import pandas as pd
# from scipy import signal
import numpy as np

# ======
# Applying filter
# ======

# # filter = signal.firwin(400, [0.01, 0.06], pass_zero=False)
# b, a = signal.ellip(8, 0.01, 200, 0.5)  # Filter to be applied.

# stdp_post_pre = pd.read_csv("C:/Users/20245580/LabCode/Codes_For_Experiments/exp_data/20250617/stdp_5.csv")

# stdp_post_pre_t = stdp_post_pre['time']
# stdp_post_pre_i = stdp_post_pre['i']
# stdp_post_pre_v = stdp_post_pre['v']

# # filtered_v = signal.convolve(stdp_post_pre_v, filter, mode='same')
# # filtered_i = signal.convolve(stdp_post_pre_i, filter, mode='same')
# filtered_v = signal.filtfilt(b, a, stdp_post_pre_v, method="gust")
# filtered_i = signal.filtfilt(b, a, stdp_post_pre_i, method="gust")

# fig, (ax1, ax2, ax3) = plt.subplots(3, 1, sharex=True)

# ax1.set_xlabel('time [s]')
# ax1.set_ylabel('v [V], no filter')
# ax1.grid()

# ax2.set_xlabel('time [s]')
# ax2.set_ylabel('v [V], filtered')
# ax2.grid()

# ax3.set_xlabel('time [s]')
# ax3.set_ylabel('i [A], filtered')
# ax3.grid()
        
# ax1.plot(stdp_post_pre_t, stdp_post_pre_v)
# ax2.plot(stdp_post_pre_t, filtered_v)
# ax3.plot(stdp_post_pre_t, filtered_i)

# plt.show()

# ======
# 3 plots
# ======
# data = pd.read_csv("C:/Users/20245580/LabCode/Codes_For_Experiments/exp_data/20251212/ecram_pulse_drain.csv")
# data = pd.read_csv("C:/Users/20245580/LabCode/Codes_For_Experiments/exp_data/20251124/ecram.csv")
data = pd.read_csv("C:/Users/20245580/LabCode/Codes_For_Experiments/exp_data/20260116/sourceAB_measureAB.csv")
stdp_post_pre_tg = data['time_g']

stdp_post_pre_t = data['time']
stdp_post_pre_i = data['i_channel']
stdp_post_pre_ig = data['i_gate']
stdp_post_pre_v = data['v_gate']


fig, (ax1, ax2, ax3) = plt.subplots(3, 1, sharex=True)

ax1.set_xlabel('time [s]')
ax1.set_ylabel('v gate [V]')
ax1.grid()

ax2.set_xlabel('time [s]')
ax2.set_ylabel('i channel [A]')
ax2.grid()

ax3.set_xlabel('time [s]')
ax3.set_ylabel('i gate [A]')
ax3.grid()

ax1.plot(stdp_post_pre_tg, stdp_post_pre_v)
ax2.plot(stdp_post_pre_t, stdp_post_pre_i)
ax3.plot(stdp_post_pre_tg, stdp_post_pre_ig)


plt.show()

# ======
# 2 plots
# ======
# data = pd.read_csv("C:/Users/20245580/LabCode/Codes_For_Experiments/exp_data/20250827/ecram_pulse_drain.csv")
# data = pd.read_csv("C:/Users/20245580/LabCode/Codes_For_Experiments/exp_data/20251111/ecram.csv")

# stdp_post_pre_t = data['time']
# stdp_post_pre_i = data['i_channel']
# stdp_post_pre_v = data['v_gate']


# fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True)

# ax1.set_xlabel('time [s]')
# ax1.set_ylabel('v gate [V]')
# ax1.grid()

# ax2.set_xlabel('time [s]')
# ax2.set_ylabel('i channel [V], filtered')
# ax2.grid()

# ax1.plot(stdp_post_pre_t, stdp_post_pre_v)
# ax2.plot(stdp_post_pre_t, stdp_post_pre_i)


# plt.show()


# ======
# 1 plots, pulse exp
# ======
# data = pd.read_csv("C:/Users/20245580/LabCode/Codes_For_Experiments\\exp_data\\20251113\\pulse_exp.csv")

# stdp_post_pre_i = data['i_channel']
# stdp_post_pre_t = np.arange(0, len(stdp_post_pre_i))#data['time']#np.arange(0, len(stdp_post_pre_i))#data['v_gate'] #np.arange(0, len(stdp_post_pre_i))#data['v_gate']

# plt.plot(stdp_post_pre_t, stdp_post_pre_i)

# plt.show()

# ======
# 1 plots, continuous source- measure 
# ======
# data = pd.read_csv("C:/Users/20245580/LabCode/Codes_For_Experiments\\exp_data\\20251209\\source_measure.csv")

# stdp_post_pre_i = data['i_channel']
# stdp_post_pre_t = data['time']#data['time']#np.arange(0, len(stdp_post_pre_i))#data['v_gate'] #np.arange(0, len(stdp_post_pre_i))#data['v_gate']

# plt.plot(stdp_post_pre_t, stdp_post_pre_i)

# plt.show()

# ======
# 2 plots, continuous source- measure 
# ======
# data = pd.read_csv("C:/Users/20245580/LabCode/Codes_For_Experiments\\exp_data\\20251212\\source_measure.csv")

# stdp_post_pre_t = data['time']
# stdp_post_pre_i = data['i_channel']
# stdp_post_pre_v = data['volt']


# fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True)

# ax1.set_xlabel('time [s]')
# ax1.set_ylabel('v gate [V]')
# ax1.grid()

# ax2.set_xlabel('time [s]')
# ax2.set_ylabel('i channel [V], filtered')
# ax2.grid()

# ax1.plot(stdp_post_pre_t, stdp_post_pre_v)
# ax2.plot(stdp_post_pre_t, stdp_post_pre_i)


# plt.show()

# ======
# 1 plots, stdp
# ======
# data = pd.read_csv("C:/Users/20245580/LabCode/Codes_For_Experiments/exp_data\\20251015\\stdp_processed_stdp_2_4D_3v1..csv")

# delta_t = data['delta']
# w_changge = data['change_percentage'] #np.arange(0, len(stdp_post_pre_i))#data['v_gate']

# plt.scatter(delta_t, w_changge)

# plt.show()

# ======
# synpase-neuron osc data plot
# ======
# data = pd.read_csv("C:/Users/20245580/LabCode/Codes_For_Experiments/exp_data/20260106\\neuron_mem.csv")

# t = data['time']
# v = data['volts']
# plt.plot(t,v)
# plt.show()