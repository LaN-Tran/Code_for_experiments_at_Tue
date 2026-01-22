# generate the the voltage sweep list
"""
    Automation Keithley 2602B, AD3
    Keithley pulse drain (smua), pulse gate (smub)
    Author:  Tran Le Phuong Lan.
    Created:  2025-09-05

    Requires:                       
       Python 2.7, 3
       pyvisa
       pyusb
       Keithley2600
    Reference:
        [1] https://github.com/LaN-Tran/Automate_Lab_Instrument/tree/main/20250905

"""

import pyvisa
import time
import logging
import csv
import os
from datetime import datetime
import numpy as np

from ctypes import *
import sys
from os import sep  

    # # ======
    # # Logger
    # # ======
# init logger
format = "%(asctime)s: %(message)s"
log_file_path = 'example.log'
logging.basicConfig(format=format, level=logging.INFO,  
                        datefmt="%H:%M:%S", filename= log_file_path, filemode= 'w')


# Gernate the sweep list, and update the file

logging.info("Prepare measurement parameters")
Vd_bias = 0.1 # [V]
Vd_pulse_on = 0.7 # [V]
pdrain_before_pgate = False

Vg_pulse_off = 0 # [V]
if (pdrain_before_pgate):
    Vg_pulse_on_I =  0 # [V]
    Vg_pulse_on_II = 0.7 # [V]
else:
    Vg_pulse_on_I =  0.7 # [V]
    Vg_pulse_on_II = 0 # [V]

t_off = 1 # [s]
t_on = 0.1 # [s]
# the reliable range of sampling speed <= 1kHz
# and the nplc must be set to 0.01 
# [Hz] (max 50kHz, depends on keithley)
time_step = 0.01 # [s]
nplc_set = 0.01 # 0.01/2 # (1 = 1/50Hz = 0.02s)
print(f"{nplc_set * (1/50)=} and {time_step=}")
if nplc_set * (1/50) > time_step:
    print("A/D speed not fast enough for the expected sampling rate")
    sys.exit(-1)

# number of recordings per phase
n_records = 5000

    # list of gate voltages for phase I
list_off_votlages = np.ones(int(t_off / time_step)) * Vg_pulse_off
list_on_votlages = np.ones(int(t_on / time_step)) * Vg_pulse_on_I
list_voltages_I = np.concatenate((list_off_votlages, list_on_votlages, list_off_votlages))

    # list of gate voltages for phase II
list_off_votlages = np.ones(int(t_off / time_step)) * Vg_pulse_off
list_on_votlages = np.ones(int(t_on / time_step)) * Vg_pulse_on_II
list_voltages_II = np.concatenate((list_off_votlages, list_on_votlages, list_off_votlages))

    # list of drain voltages
list_VDoff_votlages = np.ones(int(t_off / time_step)) * Vd_bias
list_VDon_votlages = np.ones(int(t_on / time_step)) * Vd_pulse_on
list_VDvoltages = np.concatenate((list_VDoff_votlages, list_VDon_votlages, list_VDoff_votlages))

    # checking the conditions
n_values_I = len(list_voltages_I) 
n_values_II = len(list_voltages_II)
n_values_drain = len(list_VDvoltages)
max_value_for_listv = 900
print(f"{n_values_I}, {n_values_II}, {n_values_drain} and {max_value_for_listv=}")
if (n_values_I > max_value_for_listv) or (n_values_II > max_value_for_listv) or (n_values_drain > max_value_for_listv) :
    print("TOO MANY Value for listv(\{\}) function!")
    sys.exit(-1)

logging.info("update the //ppecram.tsp// ")
print(f"{'='*5}\nupdate the //ppecram.tsp//\n{'='*5}")
filename = 'C:/Users/20245580/LabCode/Codes_For_Experiments/codes\\ppecram.tsp'
with open(filename, 'r') as file:
    lines = file.readlines()

print(f"{'='*5}\n pulse_off_drain = Vd_bias\n{'='*5}")
line_number = 14
lines[line_number-1]= 'pulse_off_drain = ' + str(Vd_bias)\
            + '\n' 

print(f"{'='*5}\n pulse_on_drain = Vd_pulse_on\n{'='*5}")
line_number = 15
lines[line_number-1]= 'pulse_on_drain = ' + str(Vd_pulse_on)\
            + '\n' 

print(f"{'='*5}\n vdrain = Vd_bias\n{'='*5}")
line_number = 16
lines[line_number-1]= 'vdrain = ' + str(Vd_bias)\
            + '\n' 

print(f"{'='*5}\n pulse_off_gate (phase I) = Vg_pulse_off\n{'='*5}")
line_number = 19
lines[line_number-1]= 'pulse_off_gate = ' + str(Vg_pulse_off)\
            + '\n' 

print(f"{'='*5}\n pulse_on_gate (phase I) = Vg_pulse_on_I\n{'='*5}")
line_number = 20
lines[line_number-1]= 'pulse_on_gate = ' + str(Vg_pulse_on_I)\
            + '\n' 

print(f"{'='*5}\n pulse_off_gate (phase II) = Vg_pulse_off\n{'='*5}")
line_number = 196
lines[line_number-1]= 'pulse_off_gate = ' + str(Vg_pulse_off)\
            + '\n' 

print(f"{'='*5}\n pulse_on_gate (phase II) = Vg_pulse_on_II\n{'='*5}")
line_number = 197
lines[line_number-1]= 'pulse_on_gate = ' + str(Vg_pulse_on_II)\
            + '\n' 

print(f"{'='*5}\n stime = time_step\n{'='*5}")
line_number = 23
lines[line_number-1]= 'stime = ' + str(time_step)\
            + '\n' 

print(f"{'='*5}\n points = n_records\n{'='*5}")
line_number = 26
lines[line_number-1]= 'points = ' + str(n_records)\
            + '\n'
 
print(f"{'='*5}\n smu_drain.trigger.source.listv(Vd_bias)\n{'='*5}")
if (pdrain_before_pgate):
    line_number = 107
    lines[line_number-1]= 'smu_drain.trigger.source.listv({' + str(list_VDvoltages.tolist()).replace("[","").replace("]","") + '})'\
            + '\n'
    line_number = 201
    lines[line_number-1]= 'smu_drain.trigger.source.listv({' + str(Vd_bias) + '})'\
            + '\n'
else:
    line_number = 201
    lines[line_number-1]= 'smu_drain.trigger.source.listv({' + str(list_VDvoltages.tolist()).replace("[","").replace("]","") + '})'\
            + '\n'
    line_number = 107
    lines[line_number-1]= 'smu_drain.trigger.source.listv({' + str(Vd_bias) + '})'\
            + '\n'

print(f"{'='*5}\n smu_gate.trigger.source.listv() (Phase I)\n{'='*5}")
line_number = 118
    # reference: strip of bracket of python list converted to string https://www.geeksforgeeks.org/python/python-remove-square-brackets-from-list/
lines[line_number-1]= 'smu_gate.trigger.source.listv({' + str(list_voltages_I.tolist()).replace("[","").replace("]","") + '})'\
            + '\n'

print(f"{'='*5}\n smu_gate.trigger.source.listv() (Phase II)\n{'='*5}")
line_number = 200
    # reference: strip of bracket of python list converted to string https://www.geeksforgeeks.org/python/python-remove-square-brackets-from-list/
lines[line_number-1]= 'smu_gate.trigger.source.listv({' + str(list_voltages_II.tolist()).replace("[","").replace("]","") + '})'\
            + '\n' 

print(f"{'='*5}\n smu_drain.measure.nplc = nplc_set\n{'='*5}")
line_number = 111
lines[line_number-1]= 'smu_drain.measure.nplc = ' + str(nplc_set)\
            + '\n'

print(f"{'='*5}\n smu_gate.measure.nplc = nplc_set\n{'='*5}")
line_number = 125
lines[line_number-1]= 'smu_gate.measure.nplc = ' + str(nplc_set)\
            + '\n' 

print(f"{'='*5}\n smu_drain.nvbuffer1.timestampresolution = time_step \n{'='*5}")
line_number = 90
lines[line_number-1]= 'smu_drain.nvbuffer1.timestampresolution = ' + str(time_step)\
            + '\n'

print(f"{'='*5}\n smu_gate.nvbuffer1.timestampresolution = time_step \n{'='*5}")
line_number = 97
lines[line_number-1]= 'smu_gate.nvbuffer1.timestampresolution = ' + str(time_step)\
            + '\n'

# Write the modified lines back to the file
with open(filename, 'w') as file:
    file.writelines(lines)
logging.info("FINISH MODIFY //ppecram.tsp//")

comment_exp = input("ENTER to START: ")

        # ======
        # Keithley, smua drain for read
        # ======
logging.info("KEITHLEY: initiate")
rm = pyvisa.ResourceManager('C:/windows/System32/visa64.dll')
keithley_instrument = rm.open_resource('USB0::0x05E6::0x2636::4480001::INSTR')
keithley_instrument.timeout = 10000
        # configure

        # ======
        # Upload the keithley scripts to keithley for the program
        # ======
# script for writing phase
logging.info("KEITHLEY: upload codes")
file_tsp_path = "C:/Users/20245580/LabCode/Codes_For_Experiments/codes\\ppecram.tsp" 
keithley_instrument.write(f"loadscript SourceRecord")
with open(file_tsp_path) as fp:
    for line in fp: keithley_instrument.write(line)
keithley_instrument.write("endscript")

        # # ======
        # # record to file
        # # ======
file_path = "C:/Users/20245580/LabCode/Codes_For_Experiments/exp_data/20260122\\ppecram.csv"
                # ======
                # Prepare record file
                # ======
logging.info("Prepare record file")
field_names = ['time_g', 'time', 'i_channel', 'v_drain', 'v_gate', 'date_time', 'comment']
if os.path.exists(file_path):
        print("File exists.")
else:
        print("File not exist. create file")
        with open(file_path, 'a') as file:
                file_writer = csv.DictWriter(file, fieldnames=field_names)
                file_writer.writeheader()
#####
# MAIN
#####
number_exps = 1
try:
    for i_exp in range(0,number_exps):
          # run keithley program
        logging.info("SourceRecord")
        print("SourceRecord phase")
        keithley_instrument.write("SourceRecord.run()") 

        print("start waiting...")
        keithley_instrument.close()
        # time.sleep(buffer_wait_time)
        # # time.sleep(t_off + t_on + t_off + t_on + t_off)
        # time.sleep(30) # [s]
        # time.sleep(buffer_wait_time)
        comment_exp = input("ENTER to END: ")
        print("end of waiting...")
        keithley_instrument = rm.open_resource('USB0::0x05E6::0x2636::4480001::INSTR')

        # record to file
        logging.info(f"Save data to file")
                    # save to file
        cur_time = 0 #time.time()
        cur_datetime = datetime.now()
        n_samples = int(float(keithley_instrument.query(f"print(smua.nvbuffer1.n)")))
        # n_samples = 1000
        print(f"{n_samples=}")
        comment_exp = ""
        for i in range(0, n_samples):
                        measured_id = float(keithley_instrument.query(f"print(smua.nvbuffer1.readings[{i}+1])"))
                        keithely_time_stamp = float(keithley_instrument.query(f"print(smua.nvbuffer1.timestamps[{i}+1])"))
                        keithely_time_stamp_g = float(keithley_instrument.query(f"print(smub.nvbuffer1.timestamps[{i}+1])"))
                        measured_vd = float(keithley_instrument.query(f"print(smua.nvbuffer1.sourcevalues[{i}+1])"))
                        measured_vg = float(keithley_instrument.query(f"print(smub.nvbuffer1.readings[{i}+1])"))
                        with open(file_path, 'a') as file: 
                                            # NOTICE: THE WHILE LOOP/ FOR LOOP INSIDE -> NO CONSTANT UPDATE TO FILE AT ALL -> NO ANIMATION
                            file_writer = csv.DictWriter(file, fieldnames=field_names)
                            info = {
                                    'time_g':cur_time + keithely_time_stamp_g,
                                    'time':cur_time + keithely_time_stamp,
                                    'i_channel': measured_id,
                                    'v_drain': measured_vd,
                                    'v_gate': measured_vg,
                                    'date_time': cur_datetime,
                                    'comment': comment_exp + '; vd: [V]' + str(Vd_bias) 
                                                + '; vg_off: [V]'+ str(Vg_pulse_off)
                                                + '; vg_on_I: [V]'+ str(Vg_pulse_on_I)
                                                + '; vg_on_II: [V]'+ str(Vg_pulse_on_II) 
                                                + '; time_step [s]: ' + str(time_step)
                                                + '; pulse_width [s]: ' + str(t_on)
                                                + '; pulse_off [s]: ' + str(t_off),


                                    }
                            file_writer.writerow(info)

        logging.info(f"Program end successfully")

except Exception as e:
      
    sys.exit(-1)
    logging.info(f"EXIT WITH ERROR")



