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

logging.info("Prepare list of voltages")
buffer_wait_time = 3 # [s]
Vd_bias = 0.05 # [V]
Vd_pulse = 0.7 # [V]
t_off = 0.5 # [s]
t_on = 0.1 # [s]
# the reliable range of sampling speed <= 1kHz
# and the nplc must be set to 0.01 
sampling_speed = 1e+2 # 10e+3 # [Hz] (max 50kHz, depends on keithley)
time_step = 1/sampling_speed
nplc_set = 0.01 # 0.01/2 # (1 = 1/50Hz = )
print(f"{nplc_set * (1/50)=} and {time_step=}")
if nplc_set * (1/50) > time_step:
    print("A/D speed not fast enough for the expected sampling rate")
    sys.exit(-1)
# keithley_instrument.query(f"print(smua.nvbuffer1.capacity )")
# the reported capacity is not applied when we use trigger to record the samples.
# the actual max samples can be recorded is around 900- 1000 (refer to factory script: SweepVListMeasureI)
max_number_samples_stored_in_keithley_internal_buffer = 900

    # list of voltages
list_off_votlages = np.ones(int(t_off / time_step)) * Vd_bias
list_on_votlages = np.ones(int(t_on / time_step)) * Vd_pulse
list_voltages = np.concatenate((list_off_votlages, list_on_votlages, list_off_votlages))
n_records = len(list_voltages) 
print(f"{n_records} and {max_number_samples_stored_in_keithley_internal_buffer=}")
if n_records > max_number_samples_stored_in_keithley_internal_buffer:
    print("TOO MANY RECORDED SAMPLES!")
    sys.exit(-1)

logging.info("update the //source_measure.tsp// ")
print(f"{'='*5}\nupdate the //source_measure.tsp//\n{'='*5}")
filename = 'C:/Users/20245580/LabCode/Codes_For_Experiments/codes\\source_measure.tsp'
# filename = 'C:/Users/20245580/LabCode/Codes_For_Experiments/codes\\sourceAB_measureA.tsp'
with open(filename, 'r') as file:
    lines = file.readlines()


    # startv =
lines[7]= 'startv = ' + str(Vd_bias)\
            + '\n' 

    # stopv =
lines[9]= 'stopv = ' + str(Vd_pulse)\
            + '\n' 

    # stime =
lines[11]= 'stime = ' + str(time_step)\
            + '\n' 
    # points =
# lines[13]= 'points = ' + str(n_records)\
#             + '\n' 

    # smu.trigger.source.listv({3, 1, 4, 5, 2})
    # reference: strip of bracket of python list converted to string https://www.geeksforgeeks.org/python/python-remove-square-brackets-from-list/
lines[65]= 'smu.trigger.source.listv({' + str(list_voltages.tolist()).replace("[","").replace("]","") + "})"\
            + '\n' 
    # smu.measure.nplc = 0.1--1
lines[77]= 'smu.measure.nplc = ' + str(nplc_set)\
            + '\n' 

# Write the modified lines back to the file
with open(filename, 'w') as file:
    file.writelines(lines)
logging.info("FINISH MODIFY //source_measure.tsp//")

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
file_tsp_path = "C:/Users/20245580/LabCode/Codes_For_Experiments/codes\\source_measure.tsp" 
# file_tsp_path = "C:/Users/20245580/LabCode/Codes_For_Experiments/codes\\sourceAB_measureA.tsp" 
keithley_instrument.write(f"loadscript SourceRecord")
with open(file_tsp_path) as fp:
    for line in fp: keithley_instrument.write(line)
keithley_instrument.write("endscript")

        # # ======
        # # record to file
        # # ======
file_path = "C:/Users/20245580/LabCode/Codes_For_Experiments/exp_data/20260119\\source_measure.csv"
                # ======
                # Prepare record file
                # ======
logging.info("Prepare record file")
field_names = ['time', 'i_channel', 'volt', 'date_time', 'comment']
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
        comment_exp = input("ENTER to end: ")
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
                        measured_i = float(keithley_instrument.query(f"print(smua.nvbuffer1.readings[{i}+1])"))
                        keithely_time_stamp = float(keithley_instrument.query(f"print(smua.nvbuffer1.timestamps[{i}+1])"))
                        measured_vd = float(keithley_instrument.query(f"print(smua.nvbuffer1.sourcevalues[{i}+1])"))
                        with open(file_path, 'a') as file: 
                                            # NOTICE: THE WHILE LOOP/ FOR LOOP INSIDE -> NO CONSTANT UPDATE TO FILE AT ALL -> NO ANIMATION
                            file_writer = csv.DictWriter(file, fieldnames=field_names)
                            info = {
                                    'time':cur_time + keithely_time_stamp,
                                    'i_channel': measured_i,
                                    'volt': measured_vd,
                                    'date_time': cur_datetime,
                                    'comment': comment_exp + '; voff: [V]' + str(Vd_bias) 
                                                + '; von: [V]'+ str(Vd_pulse) 
                                                + '; pulse_width [s]: ' + str()
                                                + '; pulse_off [s]: ' + str(t_off),

                                    }
                            file_writer.writerow(info)

        logging.info(f"Program end successfully")

except Exception as e:
      
    sys.exit(-1)
    logging.info(f"EXIT WITH ERROR")



