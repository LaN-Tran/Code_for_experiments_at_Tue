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
from scipy import signal

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
# 2 plots
# ======
# data = pd.read_csv("C:/Users/20245580/LabCode/Codes_For_Experiments/exp_data/20250702/ecram.csv")

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
# 1 plots
# ======
data = pd.read_csv("C:/Users/20245580/LabCode/Codes_For_Experiments/exp_data/20250721/transfer_curve_evaline_1_oect2_01.csv")

stdp_post_pre_t = data['v_gate']
stdp_post_pre_i = data['i_channel']


plt.plot(stdp_post_pre_t, stdp_post_pre_i)

plt.show()
