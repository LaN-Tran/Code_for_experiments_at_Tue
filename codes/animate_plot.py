"""
    Automation Keithley 2602B measurement
    Transfer curve Diode experiment
    Author:  Tran Le Phuong Lan.
    Created:  2025-09-17

    Requires:                       
       Python 2.7, 3
    Reference:

    [1] https://matplotlib.org/stable/users/explain/animations/animations.html
"""
import numpy as np
import matplotlib.pyplot as plt 
import matplotlib.animation as animation
import pandas as pd

data = pd.read_csv("C:\\Users\\20245580\\work\\Code_for_experiments_at_Tue\\exp_data\\20250918\\transfer_curve.csv")

fig, ax = plt.subplots()
t = data['v_gate']
z2 = data['i_gate']

line2 = ax.plot(t[0], z2[0], label=f'memristor')[0]
ax.set(xlim=[-2, 2], ylim=[-0.1, 0.1], xlabel='Time [s]', ylabel='Z [m]')
ax.legend()


def update(frame):
    # for each frame, update the data stored on each artist.
    # update the line plot:
    line2.set_xdata(t[:frame])
    line2.set_ydata(z2[:frame])
    return (line2)


# frames = total number of data point to plot
ani = animation.FuncAnimation(fig=fig, func=update, frames=5000, interval=30)
plt.show()