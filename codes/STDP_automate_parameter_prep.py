"""
    Automation Keithley 2602B, Arduino
    STDP
    Author:  Tran Le Phuong Lan.
    Created:  2025-10-06

    Requires:                       
        Python 2.7, 3
        pyfirmata
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


#         # # ======
#         # # Measurement setup
#         # # ======
logging.info("MEASUREMENT SETUP")

logging.info("MODIFY keithley_transfer_curve_stdp_automate.py")
    # Read file and modify content
filename = 'C:\\Users\\20245580\\work\\Code_for_experiments_at_Tue\\codes\\keithley_transfer_curve_automate_stdp.py'
with open(filename, 'r') as file:
    lines = file.readlines()

    # Modify the path for record file
print(f"{'='*5}\nTransfer curve file content modification\n{'='*5}")
print(f"!! Modify path of the recorded file")
exp_date = input("enter <date> for folder exp_data/<date>, NO SPACE: ")
lines[56]= 'file_path = \"C:/Users/20245580/work/Code_for_experiments_at_Tue/exp_data' \
                        + '/' + exp_date + '/transfer_curve.csv\"' \
                        + '\n' 

# Write the modified lines back to the file
with open(filename, 'w') as file:
    file.writelines(lines)
logging.info("FINISH MODIFY keithley_transfer_curve_stdp_automate.py")

logging.info("MODIFY single_pulse_measurement_automate_stdp.tsp")
print(f"{'='*5}\nsingle_pulse_measurement_automate_stdp.tsp\n{'='*5}")
filename = 'C:\\Users\\20245580\\work\\Code_for_experiments_at_Tue\\codes\\single_pulse_measurement_automate_stdp.tsp'
with open(filename, 'r') as file:
    lines = file.readlines()

print(f"!! read pulse amplitude, pulse width, pulse period,...")
read_pulse_amp = input("enter \\read pulse amplitude [V]\\, NO SPACE: ")
t_on = input("enter \\read pulse width [s]\\, NO SPACE: ")
t_off = input("enter \\read pulse off [s]\\, NO SPACE: ")
number_of_rpulses = input("enter \\number of read pulses\\, NO SPACE: ")
    # level
lines[14]= 'level = ' + read_pulse_amp\
            + '\n' 
    # ton
lines[16]= 'ton = ' + t_on\
            + '\n' 
    # toff
lines[18]= 'toff = ' + t_off\
            + '\n' 
    # # of rpulses
lines[20]= 'points = ' + number_of_rpulses\
            + '\n' 

# Write the modified lines back to the file
with open(filename, 'w') as file:
    file.writelines(lines)
logging.info("FINISH MODIFY single_pulse_measurement_automate_stdp.tsp")

logging.info("MODIFY multiple_pulse_measurement_automate_stdp.tsp")
print(f"{'='*5}\multiple_pulse_measurement_automate_stdp.tsp\n{'='*5}")
filename = 'C:\\Users\\20245580\\work\\Code_for_experiments_at_Tue\\codes\\multiple_pulse_measurement_automate_stdp.tsp'
with open(filename, 'r') as file:
    lines = file.readlines()

print(f"!! read pulse amplitude, pulse width, pulse period,...")
read_pulse_amp = input("enter \\read pulse amplitude [V]\\, NO SPACE: ")
t_on = input("enter \\read pulse width [s]\\, NO SPACE: ")
t_off = input("enter \\read pulse off [s]\\, NO SPACE: ")
number_of_rpulses = input("enter \\number of read pulses\\, NO SPACE: ")
    # level
lines[14]= 'level = ' + read_pulse_amp\
            + '\n' 
    # ton
lines[16]= 'ton = ' + t_on\
            + '\n' 
    # toff
lines[18]= 'toff = ' + t_off\
            + '\n' 
    # # of rpulses
lines[20]= 'points = ' + number_of_rpulses\
            + '\n' 

# Write the modified lines back to the file
with open(filename, 'w') as file:
    file.writelines(lines)
logging.info("FINISH MODIFY multiple_pulse_measurement_automate_stdp.tsp")

logging.info("MODIFY pulse_train_2ch_dg_automate_stdp.tsp")
    # Read file and modify content
print(f"{'='*5}\npulse_train_2ch_dg_automate_stdp.tsp\n{'='*5}")
filename = 'C:\\Users\\20245580\\work\\Code_for_experiments_at_Tue\\codes\\pulse_train_2ch_dg_automate_stdp.tsp'
with open(filename, 'r') as file:
    lines = file.readlines()

print(f"!! Pulse amplitude, pulse width, pulse period, delta_t")
Vd_amp = input("enter \\Vd amplitude [V]\\, NO SPACE: ")
Vg_amp = input("enter \\Vg amplitude [V]\\, NO SPACE: ")
pulse_period = input("enter \\Pulse Period [s]\\, NO SPACE: ")
pulse_width = input("enter \\Pulse Width [s]\\, NO SPACE: ")
delta_t = input("enter \\Delta_t [V]\\, NO SPACE: ")
number_of_pulses = input("enter \\Number of Pulses -1\\, NO SPACE: ")
    # Vd
lines[18]= 'pulse_vd = ' + Vd_amp\
            + '\n' 
    # Vg
lines[19]= 'pulse_vg = ' + Vg_amp\
            + '\n' 
    # pulse period
lines[39]= 'pulse_period = ' + pulse_period\
            + '\n' 
    # pulse width
lines[40]= 'pulse_width = ' + pulse_width\
            + '\n' 
    # delta_t
lines[41]= 'deta_t = ' + delta_t\
            + '\n' 
    # number of pulses
lines[44]= 'number_pulses= ' + number_of_pulses\
            + '\n' 

# Write the modified lines back to the file
with open(filename, 'w') as file:
    file.writelines(lines)
logging.info("FINISH MODIFY pulse_train_2ch_dg_automate_stdp.tsp")

logging.info("MODIFY pulse_train_2ch_gd_automate_stdp.tsp")
    # Read file and modify content
print(f"{'='*5}\npulse_train_2ch_gd_automate_stdp.tsp\n{'='*5}")
print(f"Same parameters with pulse_train_2ch_dg_automate_stdp.tsp")
filename = 'C:\\Users\\20245580\\work\\Code_for_experiments_at_Tue\\codes\\pulse_train_2ch_gd_automate_stdp.tsp'
with open(filename, 'r') as file:
    lines = file.readlines()

    # Vd
lines[18]= 'pulse_vd = ' + Vd_amp\
            + '\n' 
    # Vg
lines[19]= 'pulse_vg = ' + Vg_amp\
            + '\n' 
    # pulse period
lines[39]= 'pulse_period = ' + pulse_period\
            + '\n' 
    # pulse width
lines[40]= 'pulse_width = ' + pulse_width\
            + '\n' 
    # delta_t
lines[41]= 'deta_t = ' + delta_t\
            + '\n' 
    # number of pulses
lines[44]= 'number_pulses= ' + number_of_pulses\
            + '\n' 

# Write the modified lines back to the file
with open(filename, 'w') as file:
    file.writelines(lines)
logging.info("FINISH MODIFY pulse_train_2ch_gd_automate_stdp.tsp")

logging.info("MODIFY keithley_interchannelPulseTrain_stdp_automate.py")
    # Read file and modify content
print(f"{'='*5}\nkeithley_interchannelPulseTrain_stdp_automate.py\n{'='*5}")
filename = 'C:\\Users\\20245580\\work\\Code_for_experiments_at_Tue\\codes\\keithley_interchannelPulseTrain_stdp_automate.py'
with open(filename, 'r') as file:
    lines = file.readlines()

nexp = input("enter \\number of exps\\, NO SPACE: ")
wait_read_to_write = input("enter \\wait r-t-w [s]\\, NO SPACE: ")
wait_write_to_read = input("enter \\wait w-t-r [s]\\, NO SPACE: ")

    # Vd
lines[64]= 'vd_amplitude = ' + Vd_amp + ' # [V]'\
            + '\n' 
    # Vg
lines[65]= 'vg_amp = ' + Vg_amp + ' # [V]'\
            + '\n' 
    # w pulse period
lines[69]= 'pulse_period = ' + pulse_period + ' # [s]'\
            + '\n' 
    # w pulse width
lines[70]= 'pulse_width = ' + pulse_width + ' # [s]'\
            + '\n' 
    # delta_t
lines[71]= 'delta_tpre_tpost = ' + delta_t + ' # [s]'\
            + '\n' 
    # number of w pulses
nwp = str(int(number_of_pulses) + 1)
lines[72]= 'n_write_cycle = ' + nwp\
            + '\n' 
    # r pulse width
lines[78]= 'pulse_width_read = ' + t_on + ' # [s]'\
            + '\n' 
    # r pulse off
lines[79]= 'read_pulse_off = ' + t_off + ' # [s]'\
            + '\n' 
    # # of r pulses
lines[80]= 'number_read_pulses = ' + number_of_rpulses \
            + '\n' 
    # record file exp path
lines[87]= 'file_path = \"C:/Users/20245580/work/Code_for_experiments_at_Tue/exp_data' \
                        + '/' + exp_date + '/pulse_exp.csv\"' \
                        + '\n' 
    # record file exp_avg path
lines[88]= 'file_path_avg = \"C:/Users/20245580/work/Code_for_experiments_at_Tue/exp_data' \
                        + '/' + exp_date + '/pulse_exp_avg.csv\"' \
                        + '\n' 
    # number of exps
lines[124]= '    nexp = ' + nexp\
            + '\n' 
    # wait r-t-w
lines[126]= '    wait_between_read_and_write = ' + wait_read_to_write + ' # [s]'\
            + '\n' 
    # wait r-t-w
lines[127]= '    wait_between_exp = ' + wait_write_to_read \
            + ' # [s] = wait between write and read'\
            + '\n' 

# Write the modified lines back to the file
with open(filename, 'w') as file:
    file.writelines(lines)
logging.info("FINISH MODIFY keithley_interchannelPulseTrain_stdp_automate.py")
