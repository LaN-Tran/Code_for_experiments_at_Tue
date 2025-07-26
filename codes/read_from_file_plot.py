import csv
import pandas as pd
import matplotlib.animation as animation
import matplotlib.pyplot as plt

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


def plot_ecram (_, file_path):
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

def plot_drain_effect (_, file_path):
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
    ax2.set_ylabel('v_channel [V]')
    ax2.grid()
        
    ax1.plot(x, y)
    ax2.plot(x, y2)

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
# ======
# Ram
# ======
# file_path = "C:/Users/20245580/LabCode/Codes_For_Experiments/exp_data/20250718/ecram.csv"

# # define the figure
# # create a figure with two subplots
# fig, (ax1, ax2) = plt.subplots(2, 1)


# # the same axes initalizations as before (just now we do it for both of them)

# ani = animation.FuncAnimation(fig, plot_ecram, interval= 500, fargs= (file_path, ))
# plt.show()

# ======
# Transfer curve
# ======

file_path = "C:/Users/20245580/LabCode/Codes_For_Experiments/exp_data/20250724/transfer_curve.csv"
# the same axes initalizations as before (just now we do it for both of them)

ani = animation.FuncAnimation(plt.gcf(), plot_transfer_curve, interval= 500, fargs= (file_path, ))
plt.show()

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
# file_path = "C:/Users/20245580/LabCode/Codes_For_Experiments/exp_data/20250711/drain_effect_oect6.csv"

# # define the figure
# # create a figure with two subplots
# fig, (ax1, ax2) = plt.subplots(2, 1)


# # the same axes initalizations as before (just now we do it for both of them)

# ani = animation.FuncAnimation(fig, plot_drain_effect, interval= 500, fargs= (file_path, ))
# plt.show()

# ======
# Output curve
# ======

# file_path = "C:/Users/20245580/LabCode/Codes_For_Experiments/exp_data/20250711/output_curve.csv"
# # the same axes initalizations as before (just now we do it for both of them)

# ani = animation.FuncAnimation(plt.gcf(), plot_output_curve, interval= 500, fargs= (file_path, ))
# plt.show()

# ======
# ram keithley ad3
# ======

# file_path = "C:/Users/20245580/LabCode/Codes_For_Experiments/exp_data/20250721/ecram_keithley_AD3.csv"
# # the same axes initalizations as before (just now we do it for both of them)

# ani = animation.FuncAnimation(plt.gcf(), plot_oect_stdp, interval= 500, fargs= (file_path, ))
# plt.show()

