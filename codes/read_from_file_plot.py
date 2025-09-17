import csv
import pandas as pd
import matplotlib.animation as animation
import matplotlib.pyplot as plt
import numpy as np

# Reference
# [1] [animate a single plot](https://www.youtube.com/watch?v=Ercd-Ip5PfQ&list=PLOG3-y9fHFjkn2ug2u2fuV8T-H_H_seul&index=77)
# [1] [animate multiple subplots](https://stackoverflow.com/questions/29832055/animated-subplots-using-matplotlib)

# mock
def read_from_file_and_plot_v1 (_, file_path):
    # global file_path
    data = pd.read_csv(file_path)
    x = data['time']
    y = data['va']
        # clear
    plt.cla()
        # plot
    plt.plot(x, y)
    # return line

# mock 
def read_from_file_and_plot_v2 (_, file_path):
        # global file_path
    data = pd.read_csv(file_path)
    x = data['time']
    y = data['va']
    y2 = data['vb']

        # clear current plot
    ax1.cla()
    ax2.cla()
        # configure the plot
    for ax in [ax1, ax2]:
        ax.set_ylim(-2, 2)
        # ax.set_xlim(0, 5)
        ax.set_xlabel('time [s]')
        ax.set_ylabel('voltage [V]')
        ax.grid()
        
    ax1.plot(x, y)
    ax2.plot(x, y2)


def plot_ecram_2plots (_, file_path):
        # global file_path
    data = pd.read_csv(file_path)
    x = data['time']
    y = data['i_channel']
    y2 = data['v_gate']

        # clear current plot
    ax1.cla()
    ax2.cla()

        # configure the plot

    # ax1.set_ylim(-2, 2)
    # ax1.set_xlim(0, 5)
    ax1.set_xlabel('time [s]')
    ax1.set_ylabel('i_channel [A]')
    ax1.grid()

    ax2.set_xlabel('time [s]')
    ax2.set_ylabel('v_gate [V]')
    ax2.grid()
        
    ax1.plot(x, y)
    ax2.plot(x, y2)

def plot_ecram_3plots (_, file_path):
        # global file_path
    data = pd.read_csv(file_path)
    x = data['time']
    y = data['i_channel']
    y2 = data['v_gate']
    y3 = data['i_gate']

        # clear current plot
    ax1.cla()
    ax2.cla()
    ax3.cla()

        # configure the plot

    # ax1.set_ylim(-2, 2)
    # ax1.set_xlim(0, 5)
    ax1.set_xlabel('time [s]')
    ax1.set_ylabel('i_channel [A]')
    ax1.grid()

    ax2.set_xlabel('time [s]')
    ax2.set_ylabel('v_gate [V]')
    ax2.grid()

    ax3.set_xlabel('time [s]')
    ax3.set_ylabel('i_gate [A]')
    ax3.grid()
        
    ax1.plot(x, y)
    ax2.plot(x, y2)
    ax3.plot(x, y3)

def plot_ecram_4plots (_, file_path):
        # global file_path
    data = pd.read_csv(file_path)
    x = data['time']
    y = data['i_channel']
    y2 = data['v_gate']
    y3 = data['i_gate']
    y4 = data['v_drain']

        # clear current plot
    ax1.cla()
    ax2.cla()
    ax3.cla()
    ax4.cla()

        # configure the plot

    # ax1.set_ylim(-2, 2)
    # ax1.set_xlim(0, 5)
    ax1.set_xlabel('time [s]')
    ax1.set_ylabel('i_channel [A]')
    ax1.grid()

    ax2.set_xlabel('time [s]')
    ax2.set_ylabel('v_gate [V]')
    ax2.grid()

    ax3.set_xlabel('time [s]')
    ax3.set_ylabel('i_gate [A]')
    ax3.grid()

    ax4.set_xlabel('time [s]')
    ax4.set_ylabel('v_drain [A]')
    ax4.grid()
        
    ax1.plot(x, y)
    ax2.plot(x, y2)
    ax3.plot(x, y3)
    ax4.plot(x, y4)

def plot_drain_effect (_, file_path):
# global file_path
    data = pd.read_csv(file_path)
    x = data['time']
    y = data['i_channel']
        # clear
    plt.cla()
        # plot
    plt.plot(x, y)
    # return line

def plot_wavegen_test (_, file_path):
        # global file_path
    data = pd.read_csv(file_path)
    x = data['time']
    y = data['v']
    y2 = data['i']

        # clear current plot
    ax1.cla()
    ax2.cla()

        # configure the plot

    # ax1.set_ylim(-2, 2)
    # ax1.set_xlim(0, 5)
    ax1.set_xlabel('time [s]')
    ax1.set_ylabel('i_channel [A]')
    ax1.grid()

    ax2.set_xlabel('time [s]')
    ax2.set_ylabel('v_gate [V]')
    ax2.grid()
        
    ax1.plot(x, y)
    ax2.plot(x, y2)

# ec-ram
def read_from_file_and_plot_ec_ram (_, file_path):
    # global file_path
    data = pd.read_csv(file_path)
    x = data['v_gate']
    y = data['i_gate']
        # clear
    plt.cla()
        # plot
    y = abs(y)
    plt.yscale('log')
    plt.plot(x, y)
    # return line

def plot_transfer_curve (_, file_path):
    # global file_path
    data = pd.read_csv(file_path)
    x = data['v_gate']
    y = data['i_channel']
        # clear
    plt.cla()
        # plot
    plt.xlabel('Vgate [V]')
    plt.ylabel('Id [A]')
    plt.plot(x, y)
    # return line

def plot_transfer_curve_2plot (_, file_path):
    # global file_path
    data = pd.read_csv(file_path)
    x = data['time']
    y = data['i_channel']
    y2 = data['v_gate']
    y3 = data['i_gate']
    y4 = data['v_drain']

        # clear current plot
    ax1.cla()
    ax2.cla()

        # configure the plot

    # ax1.set_ylim(-2, 2)
    # ax1.set_xlim(0, 5)
    ax1.set_xlabel('Vg [V]')
    ax1.set_ylabel('i_channel [A]')
    ax1.grid()

    ax2.set_xlabel('Vg [V]')
    ax2.set_ylabel('i_gate [A]')
    ax2.grid()
        
    ax1.plot(y2, y)
    ax2.plot(y2, y3)

def plot_transfer_curve_diode (_, file_path):
    # global file_path
    data = pd.read_csv(file_path)
    x = data['v_drain']
    y = data['i_channel']
        # clear
    plt.cla()
        # plot
    plt.plot(x, y)
    
    # return line

def plot_output_curve (_, file_path):
    # global file_path
    data = pd.read_csv(file_path)
    x = data['v_drain']
    y = data['i_channel']
        # clear
    plt.cla()
        # plot
    plt.plot(x, y)
    # return line

def plot_oect_stdp (_, file_path):
    # global file_path
    data = pd.read_csv(file_path)
    x = data['time']
    y = data['i_channel']
        # clear
    plt.cla()
        # plot
    plt.plot(x, y)
    # return line

def k_pulse_read (_, file_path):
    # global file_path
    data = pd.read_csv(file_path)
    # x = data['time']
    # y = data['i_channel']
    y = data['i_channel_avg']
        # clear
    plt.cla()
        # plot
    x = np.arange(0, len(y))
    plt.plot(x, y)
    # return line
# ======
# Ram, 2 plot
# ======
# file_path = "C:/Users/20245580/LabCode/Codes_For_Experiments/exp_data/20250901/ecram.csv"

# # define the figure
# # create a figure with two subplots
# fig, (ax1, ax2) = plt.subplots(2, 1)


# # the same axes initalizations as before (just now we do it for both of them)

# ani = animation.FuncAnimation(fig, plot_ecram_2plots, interval= 500, fargs= (file_path, ))
# plt.show()

# # ======
# # Ram, 3 plot
# # ======
# file_path = "C:/Users/20245580/LabCode/Codes_For_Experiments/exp_data/20250828/ecram_pulse_drain.csv"

# # define the figure
# # create a figure with two subplots
# fig, (ax1, ax2, ax3) = plt.subplots(3, 1)


# # the same axes initalizations as before (just now we do it for both of them)

# ani = animation.FuncAnimation(fig, plot_ecram_3plots, interval= 500, fargs= (file_path, ))
# plt.show()

# ======
# Ram, 4 plot
# ======
# file_path = "C:/Users/20245580/LabCode/Codes_For_Experiments/exp_data/20250912/ecram_pulse_drain.csv"
# # file_path = "C:/Users/20245580/LabCode/Codes_For_Experiments/exp_data/20250901/ecram.csv"

# # define the figure
# # create a figure with two subplots
# fig, (ax1, ax2, ax3, ax4) = plt.subplots(4, 1)


# # the same axes initalizations as before (just now we do it for both of them)

# ani = animation.FuncAnimation(fig, plot_ecram_4plots, interval= 500, fargs= (file_path, ))
# plt.show()
# ======
# Transfer curve
# ======

file_path = "C://Users//20245580//work//Code_for_experiments_at_Tue//exp_data//20250917//transfer_curve.csv"
# the same axes initalizations as before (just now we do it for both of them)

# define the figure
# create a figure with two subplots
fig, (ax1, ax2) = plt.subplots(1, 2)

# ani = animation.FuncAnimation(plt.gcf(), plot_transfer_curve, interval= 500, fargs= (file_path, ))
ani = animation.FuncAnimation(plt.gcf(), plot_transfer_curve_2plot, interval= 500, fargs= (file_path, ))
plt.show()

# ======
# Transfer curve, diode
# ======

# file_path = "C:/Users/20245580/LabCode/Codes_For_Experiments/exp_data/20250822/transfer_curve_diode.csv"
# # the same axes initalizations as before (just now we do it for both of them)

# ani = animation.FuncAnimation(plt.gcf(), plot_transfer_curve_diode, interval= 500, fargs= (file_path, ))
# plt.show()

# ======
# Oect stdp
# ======

# file_path = "C:/Users/20245580/LabCode/Codes_For_Experiments/exp_data/20250703/stdp_oect6.csv"
# # the same axes initalizations as before (just now we do it for both of them)

# ani = animation.FuncAnimation(plt.gcf(), plot_oect_stdp, interval= 500, fargs= (file_path, ))
# plt.show()

# ======
# Drain effect
# ======
# file_path = "C:/Users/20245580/LabCode/Codes_For_Experiments/exp_data/20250807/drain_effect.csv"
# # the same axes initalizations as before (just now we do it for both of them)

# ani = animation.FuncAnimation(plt.gcf(), plot_drain_effect, interval= 500, fargs= (file_path, ))
# plt.show()

# ======
# Output curve
# ======

# file_path = "C:/Users/20245580/LabCode/Codes_For_Experiments/exp_data/20250711/output_curve.csv"
# # the same axes initalizations as before (just now we do it for both of them)

# ani = animation.FuncAnimation(plt.gcf(), plot_output_curve, interval= 500, fargs= (file_path, ))
# plt.show()

# ======
# keithley pulse read ad3
# ======

# file_path = "C:/Users/20245580/LabCode/Codes_For_Experiments/exp_data/20250912/pulse_exp_avg.csv"
# # the same axes initalizations as before (just now we do it for both of them)

# ani = animation.FuncAnimation(plt.gcf(), k_pulse_read, interval= 500, fargs= (file_path, ))
# plt.show()

