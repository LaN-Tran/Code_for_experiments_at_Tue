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
import matplotlib.animation as animation
import math
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
# data = pd.read_csv("C:/Users/20245580/LabCode/Codes_For_Experiments/exp_data/20260629/ecram_3Tmem_pg2ttt_gel_s1_fineGateShortS_91.csv")
data = pd.read_csv("C:/Users/20245580/LabCode/Codes_For_Experiments/exp_data/20260408/ecram.csv")
# # # data = pd.read_csv("C:/Users/20245580/LabCode/Codes_For_Experiments/exp_data/20260116/sourceAB_measureAB.csv")
# # # stdp_post_pre_tg = data['time_g']

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

ax1.plot(stdp_post_pre_t, stdp_post_pre_v)
ax2.plot(stdp_post_pre_t, stdp_post_pre_i)
ax3.plot(stdp_post_pre_t, stdp_post_pre_ig)

plt.show()

# ======
# 4 plots
# ======
# data = pd.read_csv("C:/Users/20245580/LabCode/Codes_For_Experiments/exp_data/20260629/ecram_3Tmem_pg2ttt_gel_s1_fineGateShortS_91.csv")
# # data = pd.read_csv("C:/Users/20245580/LabCode/Codes_For_Experiments/exp_data/20260408/ecram.csv")
# # # # data = pd.read_csv("C:/Users/20245580/LabCode/Codes_For_Experiments/exp_data/20260116/sourceAB_measureAB.csv")
# # # # stdp_post_pre_tg = data['time_g']

# stdp_post_pre_t = data['time']
# stdp_post_pre_i = data['i_channel']
# stdp_post_pre_ig = data['i_gate']
# stdp_post_pre_v = data['v_gate']
# stdp_post_pre_vd = data['v_drain']

# fig, (ax1, ax2, ax3, ax4) = plt.subplots(4, 1, sharex=True)

# ax1.set_xlabel('time [s]')
# ax1.set_ylabel('v gate [V]')
# ax1.grid()

# ax2.set_xlabel('time [s]')
# ax2.set_ylabel('i channel [A]')
# ax2.grid()

# ax3.set_xlabel('time [s]')
# ax3.set_ylabel('i gate [A]')
# ax3.grid()

# ax4.set_xlabel('time [s]')
# ax4.set_ylabel('v drain [V]')
# ax4.grid()

# ax1.plot(stdp_post_pre_t, stdp_post_pre_v)
# ax2.plot(stdp_post_pre_t, stdp_post_pre_i)
# ax3.plot(stdp_post_pre_t, stdp_post_pre_ig)
# ax4.plot(stdp_post_pre_t, stdp_post_pre_vd)
# plt.show()

# ======
# 2 plots
# ======
# data = pd.read_csv("C:/Users/20245580/LabCode/Codes_For_Experiments/exp_data/20260611/ecram_20250611_SExtWithFineGate_Dr-SMUApulse_pg2ttt_gatech_nacl_s1_62.csv")
# # # data = pd.read_csv("C:/Users/20245580/LabCode/Codes_For_Experiments/exp_data/20260408/ecram.csv")
# # # data = pd.read_csv("C:/Users/20245580/LabCode/Codes_For_Experiments/exp_data/20260116/sourceAB_measureAB.csv")
# # # stdp_post_pre_tg = data['time_g']

# stdp_post_pre_t = data['time']
# stdp_post_pre_i = data['i_channel']
# stdp_post_pre_ig = data['i_gate']
# stdp_post_pre_v = data['v_gate']
# stdp_post_pre_vd = data['v_drain']

# fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True)

# ax1.set_xlabel('time [s]')
# ax1.set_ylabel('v [V]')
# ax1.grid()

# ax2.set_xlabel('time [s]')
# ax2.set_ylabel('i [A]')
# ax2.grid()

# ax1.plot(stdp_post_pre_t, stdp_post_pre_v)
# ax2.plot(stdp_post_pre_t, stdp_post_pre_ig)
# plt.show()

# ======
# 2 plots
# ======
# data = pd.read_csv("C:/Users/20245580/LabCode/Codes_For_Experiments/exp_data/20250827/ecram_pulse_drain.csv")
# # data = pd.read_csv("C:/Users/20245580/LabCode/Codes_For_Experiments/exp_data/20251111/ecram.csv")
# # data = pd.read_csv("C:/Users/20245580/LabCode/Codes_For_Experiments/exp_data/20260116/sourceAB_measureAB.csv")
# # stdp_post_pre_tg = data['time_g']
# # stdp_post_pre_v = data['v_gate']

# data = pd.read_csv("C:/Users/20245580/LabCode/Codes_For_Experiments/exp_data/20260121/source_measure_80_Diode_Gate.csv")

# stdp_post_pre_t = data['time']
# stdp_post_pre_i = data['i_channel']
# stdp_post_pre_v = data['volt']

# fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True)

# ax1.set_xlabel('time [s]')
# # ax1.set_ylabel('v gate [V]')
# ax1.set_ylabel('v drain [V]')
# ax1.grid()

# ax2.set_xlabel('time [s]')
# ax2.set_ylabel('i channel [V]')
# ax2.grid()

# # ax1.plot(stdp_post_pre_tg, stdp_post_pre_v)
# # ax1.plot(stdp_post_pre_t, stdp_post_pre_v)

# ax1.plot(stdp_post_pre_t, stdp_post_pre_v)
# ax2.plot(stdp_post_pre_t, stdp_post_pre_i)


# plt.show()

# ======
# 2 plots, transfer curve i-v
# ======
# device = pd.read_csv("C:/Users/20245580/LabCode/Codes_For_Experiments/exp_data/20260701/transfer_curve_20260701_2T_pv2-2_nacl_BigGateShortS_11.csv")

# device_ich = device['i_channel']
# device_ig = device['i_gate']
# device_vg = device['v_gate']

# fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True)

# ax1.set_xlabel('V [V]')
# # ax1.set_ylabel('v gate [V]')
# ax1.set_ylabel('I [A]')
# ax1.grid()

# ax2.set_xlabel('V [V]')
# ax2.set_ylabel('I [A]')
# ax2.grid()

# # device_ich=abs(device_ich)  # <-- Take the absolute value of the current
# # ax1.set_yscale('log')  # <-- Converts y-axis to log scale
# ax1.plot(device_vg, device_ig)

# device_ig=abs(device_ig)  # <-- Take the absolute value of the current
# ax2.set_yscale('log')  # <-- Converts y-axis to log scale
# ax2.plot(device_vg, device_ig)


# plt.show()

# ======
# 2 plots, transfer curve i_vs_t & v_vs_t in the same plot
# ======

# using twinx() for plotting two y-axes on the same plot
# reference: https://matplotlib.org/stable/gallery/subplots_axes_and_figures/multiple_yaxis_with_spines.html
# device = pd.read_csv("C:/Users/20245580/LabCode/Codes_For_Experiments/exp_data/20260604/transfer_curve_20260604_2terminalGate_T1gateShortS-GND_T2gateSMUB_drSMUA_pdpss_gatech_nacl_s1_22.csv")

# device_t = device['time']
# device_ich = device['i_channel']
# device_ig = device['i_gate']
# device_vg = device['v_gate']

# fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True)

# twin1_ax1 = ax1.twinx()
# ax1.set_xlabel('t [s]')
# # ax1.set_ylabel('v gate [V]')
# ax1.set_ylabel('Id [A], Vgs [V] ')
# ax1.grid()

# twin1_ax2 = ax2.twinx()
# ax2.set_xlabel('t [s]')
# ax2.set_ylabel('Ig [A], Vgs [V]')
# ax2.grid()

# # device_ich=abs(device_ich)  # <-- Take the absolute value of the current
# # ax1.set_yscale('log')  # <-- Converts y-axis to log scale
# ax1.plot(device_t, device_ich)
# twin1_ax1.plot(device_t, device_vg, color='orange')
# # ax1.plot(device_t, device_vg)

# # device_ig=abs(device_ig)  # <-- Take the absolute value of the current
# # ax2.set_yscale('log')  # <-- Converts y-axis to log scale
# ax2.plot(device_t, device_ig)
# twin1_ax2.plot(device_t, device_vg, color='orange')

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
# data = pd.read_csv("C:/Users/20245580/LabCode/Codes_For_Experiments\\exp_data\\20260119\\source_measure.csv")

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
# data = pd.read_csv("C:/Users/20245580/LabCode/Codes_For_Experiments/exp_data/20260327\\neuron_mem.csv")

# t = data['time']
# v = data['volts']
# plt.plot(t,v)
# plt.show()


# ======
# 2 plots, ppecram.tsp - ppecram.py
# ======
# data = pd.read_csv("C:/Users/20245580/LabCode/Codes_For_Experiments/exp_data/20250827/ecram_pulse_drain.csv")
# data = pd.read_csv("C:/Users/20245580/LabCode/Codes_For_Experiments/exp_data/20251111/ecram.csv")
# data = pd.read_csv("C:/Users/20245580/LabCode/Codes_For_Experiments/exp_data/20260116/sourceAB_measureAB.csv")
# stdp_post_pre_tg = data['time_g']
# stdp_post_pre_v = data['v_gate']

# data = pd.read_csv("C:/Users/20245580/LabCode/Codes_For_Experiments/exp_data/20260126/ppecram.csv")

# stdp_post_pre_tg = data['time_g']
# stdp_post_pre_t = data['time']
# stdp_post_pre_i = data['i_channel']
# stdp_post_pre_vg = data['v_gate']
# stdp_post_pre_vd = data['v_drain']

# fig, (ax1, ax2, ax3) = plt.subplots(3, 1, sharex=True)

# ax1.set_xlabel('time [s]')
# # ax1.set_ylabel('v gate [V]')
# ax1.set_ylabel('v gate [V]')
# ax1.grid()

# ax2.set_xlabel('time [s]')
# ax2.set_ylabel('i channel [V]')
# ax2.grid()

# ax3.set_xlabel('time [s]')
# ax3.set_ylabel('vd [V]')
# ax3.grid()

# ax1.plot(stdp_post_pre_tg, stdp_post_pre_vg)
# ax3.plot(stdp_post_pre_t, stdp_post_pre_vd)
# ax2.plot(stdp_post_pre_t, stdp_post_pre_i)

# plt.show()

#===========
# animate the transfer curve plot 
#===========

# # Sample data
# device = pd.read_csv("C:/Users/20245580/LabCode/Codes_For_Experiments/exp_data/20260701/transfer_curve_20260701_2T_pv2-2_nacl_BigGateShortS_11.csv")

# device_t = device['time']
# device_ig = device['i_gate']
# device_vg = device['v_gate']

# print(device_ig.min(), device_ig.max())
# print(device_vg.min(), device_vg.max())

# # Set up figure
# fig, ax = plt.subplots()
# ax.set_xlim(-1, 1)
# ax.set_ylim(-0.0015, 0.0021)
# ax.set_xlabel("Time (s)")
# ax.set_ylabel("Value")

# line, = ax.plot([], [], lw=1)

# def init():
#     line.set_data([], [])
#     return line,

# def update(frame):
#     # Show data up to current frame
#     line.set_data(device_vg[:frame], device_ig[:frame])
#     return line,

# ani = animation.FuncAnimation(
#     fig, update, frames=len(device_vg),
#     init_func=init, blit=False, interval=100
# )

# ani.save("C:/Users/20245580/LabCode/Codes_For_Experiments/exp_data/20260701/transfer_curve_20260701_2T_pv2-2_nacl_BigGateShortS_11.gif", writer="pillow", fps=60)

# plt.show()

#===========
# animate the transfer curve (2T memristor) plot produced by the Tu/e yoeri neuro group- matlab transfer curve code 
# with 2 subplots
#===========
# # # =======
# # # Charles ionic diode data
# # data = np.loadtxt(r"C:\Users\20245580\LabCode\Codes_For_Experiments\exp_data\Charles_ionic_diode.txt", delimiter="\t")
# # # print(data.shape)
# # device_ig = data[:, 4]
# # device_ig_abs = np.abs(device_ig)
# # device_vg = data[:, 2]

# # # =======
# # # normal transfer curve data
# # device = pd.read_csv("C:/Users/20245580/LabCode/Codes_For_Experiments/exp_data/20260629/transfer_curve_20260629_2Tmem_pg2ttt_gel_s1_fineGateShortS_51.csv")

# # device_t = device['time']
# # device_ig = device['i_gate']
# # device_ig_abs = np.abs(device_ig)
# # device_vg = device['v_gate']

# # =======
# # normal transfer curve data - oect profiling code
# file_name = "transfer_curve_20260721_vi_2T_pg2ttt_s3_nacl_13.csv"
# file_path = f"C:/Users/20245580/LabCode/Codes_For_Experiments/exp_data/20260518/{file_name}"
# save_path = f"C:/Users/20245580/LabCode/Codes_For_Experiments/exp_data/20260518/{file_name.replace('.csv', '.gif')}"
# device = pd.read_csv(file_path)

# device_t = device['time']
# device_ig = device['i_channel']
# device_ig_abs = np.abs(device_ig)
# device_vg = device['v_drain']

# print(f"Y axis: {device_ig.min()=}, {device_ig.max()=}")
# print(f"X axis: {device_vg.min()=}, {device_vg.max()=}")
# print(f"Absolute Y axis: {device_ig_abs.min()=}, {device_ig_abs.max()=}")
# # t = np.linspace(0, 10, 200)
# # y = np.sin(t)

# # Set up figure
# fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True)

# x_decimal_places = 1e+1
# y_decimal_places = 1e+3
# ax1.set_ylim(device_ig.min()-(1/y_decimal_places), 
#              device_ig.max()+(1/y_decimal_places))
# ax1.set_xlim(device_vg.min()-(1/x_decimal_places), 
#              device_vg.max()+(1/x_decimal_places))
# ax1.set_xlabel("V (V)")
# ax1.set_ylabel("I (A)")

# ax2.set_ylim(device_ig_abs.min()/10, 
#              device_ig_abs.max()*10)
# ax2.set_yscale('log')

# line, = ax1.plot([], [], lw=1)
# line2, = ax2.plot([], [], lw=1)

# def init():
#     line.set_data([], [])
#     line2.set_data([], [])
#     return line, line2

# def update(frame):
#     # Show data up to current frame
#     line.set_data(device_vg[:frame], device_ig[:frame])
#     line2.set_data(device_vg[:frame], device_ig_abs[:frame])
#     return line,

# ani = animation.FuncAnimation(
#     fig, update, frames=len(device_vg),
#     init_func=init, blit=False, interval=100
# )

# # # # =======
# # # # Charles ionic diode data
# # # ani.save("C:/Users/20245580/LabCode/Codes_For_Experiments/exp_data/Charles_ionic_diode.gif", writer="pillow", fps=60)

# # ani.save("C:/Users/20245580/LabCode/Codes_For_Experiments/exp_data/20260629/transfer_curve_20260629_2Tmem_pg2ttt_gel_s1_fineGateShortS_51.gif", writer="pillow", fps=60)
# # plt.show()

# ani.save(save_path, writer="pillow", fps=60)
# plt.show()

#===========
# animate the transfer curve (3T memristor) plot produced by the Tu/e yoeri neuro group- matlab transfer curve code 
# with 3 subplots
#===========

# device = pd.read_csv("C:/Users/20245580/LabCode/Codes_For_Experiments/exp_data/20260629/transfer_curve_20260629_3Tmem_pg2ttt_nacl_s1_fineGateShortS_11.csv")

# device_t = device['time']
# device_ig = device['i_gate']
# device_id = device['i_channel']
# device_ig_abs = np.abs(device_ig)
# device_vg = device['v_gate']

# print(f"Gate current: {device_ig.min()=}, {device_ig.max()=}")
# print(f"Channel current: {device_id.min()=}, {device_id.max()=}")
# print(f"Gate voltage: {device_vg.min()=}, {device_vg.max()=}")
# print(f"Absolute gate current: {device_ig_abs.min()=}, {device_ig_abs.max()=}")
# # t = np.linspace(0, 10, 200)
# # y = np.sin(t)

# # Set up figure
# fig, axs = plt.subplots(2, 2, sharex=True)

# axs[0, 0].set_ylim(-8.7e-05, 0.0012)
# axs[0, 0].set_xlim(-1, 1.1)
# axs[0, 0].set_xlabel("Vg (V)")
# axs[0, 0].set_ylabel("Ig (A)")

# axs[1, 0].set_ylim(1e-7, 0.0012)
# axs[1, 0].set_yscale('log')
# axs[1, 0].set_ylabel("log(Ig) (A)")

# axs[0, 1].set_ylim(3.2e-05, 0.00021)
# axs[0, 1].set_xlim(-1, 1.1)
# axs[0, 1].set_xlabel("Vg (V)")
# axs[0, 1].set_ylabel("Id @Vd=0.2V (A)")

# line, = axs[0, 0].plot([], [], lw=1)
# line3, = axs[1, 0].plot([], [], lw=1)
# line4, = axs[0, 1].plot([], [], lw=1)

# def init():
#     line.set_data([], [])
#     line3.set_data([], [])
#     line4.set_data([], [])
#     return line, line3, line4

# def update(frame):
#     # Show data up to current frame
#     line.set_data(device_vg[:frame], device_ig[:frame])
#     line3.set_data(device_vg[:frame], device_ig_abs[:frame])
#     line4.set_data(device_vg[:frame], device_id[:frame])
#     return line, line3, line4

# ani = animation.FuncAnimation(
#     fig, update, frames=len(device_vg),
#     init_func=init, blit=False, interval=100
# )

# ani.save("C:/Users/20245580/LabCode/Codes_For_Experiments/exp_data/20260629/transfer_curve_20260629_3Tmem_pg2ttt_nacl_s1_fineGateShortS_11.gif", writer="pillow", fps=60)
# plt.show()