"""
    Automation Keithley 2602B, Arduino
    STDP
    Author:  Tran Le Phuong Lan.
    Created:  2025-10-06

    Requires:                       
        Python 2.7, 3
        keithley_transfer_curve_stdp_automate.py
        keithley_interchannelPulseTrain_dg_stdp_automate.py
            pulse_train_2ch_dg_automate_stdp.py
        keithley_interchannelPulseTrain_gd_stdp_automate.py
            pulse_train_2ch_gd_automate_stdp.py
        single_pulse_measurement_automate_stdp.py

    Reference:

"""
import time
import logging
import pyfirmata
import csv
from datetime import datetime

    # # ======
    # # Logger
    # # ======
# init logger
format = "%(asctime)s: %(message)s"
log_file_path = 'example.log'
logging.basicConfig(format=format, level=logging.INFO,  
                        datefmt="%H:%M:%S", filename= log_file_path, filemode= 'w')

        # # ======
        # # Arduino board, change between read and write
        # # ======
logging.info("configure arduino mux")
    # MUX 1 (Y0: transfer curve, Y1: ecram)
# arduino_bin_mux1_z =  3# 

# arduino_bin_mux1_s0 = 5 # (lsb)
# arduino_bin_mux1_s1 = 7 #
# arduino_bin_mux1_s2 = 9 # (msb)

# arduino_bin_mux1_enable = 11 #

#     # MUX 2 (Y0: transfer curve, Y1: ecram)
# arduino_bin_mux2_z = 2 # (HIGH = OFF/ LOW = ON)

# arduino_bin_mux2_s0 = 4 # (lsb)
# arduino_bin_mux2_s1 = 6 #
# arduino_bin_mux2_s2 = 8 # (msb)

# arduino_bin_mux2_enable = 10 #
#     # init arduino aboard
# arduino_board = pyfirmata.Arduino('COM8')

#         # # ======
#         # # Measurement 
#         # # ======
# logging.info("Measurement start")

# # transfer curve sweep setup and run
# logging.info("Configure to transfer curve setup")
# # # arduino mux1 connect to Y0
#         # Y0 configure
# arduino_board.digital[arduino_bin_mux1_s0].write(0)
# arduino_board.digital[arduino_bin_mux1_s1].write(0)
# arduino_board.digital[arduino_bin_mux1_s2].write(0)
#         # close switch
# arduino_board.digital[arduino_bin_mux1_enable].write(0)
# time.sleep(arduino_settle_time)

# # # arduino mux2 connect to Y0
#         # Y0 configure
# arduino_board.digital[arduino_bin_mux2_s0].write(0)
# arduino_board.digital[arduino_bin_mux2_s1].write(0)
# arduino_board.digital[arduino_bin_mux2_s2].write(0)
#         # close switch
# arduino_board.digital[arduino_bin_mux2_enable].write(0)
# time.sleep(arduino_settle_time)

# # Modify ``keithley_transfer_curve_stdp_automate.py``
    # Read file and modify content
filename = 'C:\\Users\\20245580\\LabCode\\Codes_For_Experiments\\codes\\keithley_transfer_curve_stdp_automate.py'
with open(filename, 'r') as file:
    lines = file.readlines()

    # Modify the path for record file
print(f"{'='*5}\nTransfer curve file content modification\n{'='*5}")
exp_date = input("enter <date> for folder exp_data/<date>: ")
lines[56]= 'file_path = \"C:/Users/20245580/LabCode/Codes_For_Experiments/exp_data' \
                        + '/' + exp_date + '/transfer_curve.csv\"' \
                        + '\n' 
# print(f"{lines[56]=}")
# for i, line in enumerate(lines):
#     # if target_text in line:
#     #     lines[i] = new_line + '\n'  # Replace the line
#     #     break  # Remove this break if you want to replace all matching lines
#     print(f"line number {i}, content:\n{line}")
#     print(type(line))

#     if i == 3:
#         value = 0.1616161
#         lines[i] = 'deta_t = ' + str(value) + '\n'  
#         break

# Write the modified lines back to the file
with open(filename, 'w') as file:
    file.writelines(lines)

    # fixed at Vg 0, and Vd @ read voltage = run code `keithley_transfer_curve_without_switch_LAN.py`
# change setup to ecram 
    # perform 1 time stdp:
        # measure the initial current -> inital g_init
        # 5x exp results: run code `keithley_interchannelPulseTrain_dg.py`/ `keithley_interchannelPulseTrain_gd.py`
            # record the voltage pulse (amplitude, pulse width, pulse periode, # of pulses) + delta (t_pre-t_post)
        # run code `?` to only measured the g_after.. in a duration of 20min -> collect an array of g_after
        # process the array of g_after to array of percentage of change (g_after's - g_init)/ g_init
            # record this array of g_after's + time 
        # process average (of array percentage of change) 
            # record average (of array percentage of change) + delta -> a fully stdp file