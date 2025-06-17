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

# transfer curve
def read_from_file_and_plot_v3 (_, file_path):
        # global file_path
    data = pd.read_csv(file_path)
    x = data['v_gate']
    y = data['i_channel']
    y2 = data['i_gate']

        # clear current plot
    ax1.cla()
    ax2.cla()

        # configure the plot

    # ax1.set_ylim(-2, 2)
    # ax1.set_xlim(0, 5)
    ax1.set_xlabel('Vg [V]')
    ax1.set_ylabel('id [A]')
    ax1.grid()

    ax2.set_xlabel('Vg [V]')
    ax2.set_ylabel('ig [A]')
    ax2.grid()
        
    ax1.plot(x, y)
    ax2.plot(x, y2)

# stdp, `stdp_record.py`
def read_from_file_and_plot_v4 (_, file_path):
        # global file_path
    data = pd.read_csv(file_path)
    x = data['time']
    y = data['i']
    y2 = data['v']

        # clear current plot
    ax1.cla()
    ax2.cla()

        # configure the plot

    # ax1.set_ylim(-2, 2)
    # ax1.set_xlim(0, 5)
    ax1.set_xlabel('time [s]')
    ax1.set_ylabel('i [A]')
    ax1.grid()

    ax2.set_xlabel('time [s]')
    ax2.set_ylabel('v [V]')
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



# file_path = "C:/Users/20245580/LabCode/Automate_Lab_Instrument/20250605/output_exp2.csv"
# file_path = "C:/Users/20245580/LabCode/Automate_Lab_Instrument/20250605/output_exp3.csv"
# file_path = "C:/Users/20245580/LabCode/Automate_Lab_Instrument/20250605/output_exp_ecram.csv"
# file_path = "C:/Users/20245580/LabCode/Codes_For_Experiments/exp_data/20250613/transfer_curve_2Metal.csv"
file_path = "C:/Users/20245580/LabCode/Codes_For_Experiments/exp_data/20250617/real_exp_stdp.csv"

# define the figure
# create a figure with two subplots
fig, (ax1, ax2) = plt.subplots(2, 1)


# the same axes initalizations as before (just now we do it for both of them)

ani = animation.FuncAnimation(fig, read_from_file_and_plot_v4, interval= 500, fargs= (file_path, ))
# ani = animation.FuncAnimation(plt.gcf(), read_from_file_and_plot_ec_ram, interval= 1000, fargs= (file_path, ))
plt.show()

