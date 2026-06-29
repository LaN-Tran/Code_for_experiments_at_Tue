# generate the the voltage sweep list
"""
    Automation Keithley 2602B
    OECT PROFILING -TRANSFER MEASUREMENT
    sweep vgs, measure ids, fixed vds
    Author:  Tran Le Phuong Lan.
    Created:  2026-05-14

    Requires:                       
       Python 2.7, 3
       pyvisa
       ?? pyusb
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


# ======
# Set parameters, Generate the sweep list
# ======
logging.info("Prepare list of voltages")
    # GATE - SMUB
number_of_sweeps = 3
scan_rate = 1 # [V/s] # 0.1 = the min scan rate
sampling_speed = 100 # 10e+3 # [Hz] (max 50kHz, depends on keithley)
time_step = 1/sampling_speed
volt_step = time_step * scan_rate
# `Vd_str` MUST < `Vd_stop`, otherwise cause error in list generation `list_fvotl`, `list_bvotl` below
vg_str = -0.6 # [V] 
vg_stop = 0.6 # [V]
    # time step limit check
nplc_set = 0.1 # 0.01/2 # (1 = 1/50Hz = )
print(f"{nplc_set * (1/50)=} and {time_step=}")
if nplc_set * (1/50) > time_step:
    print("A/D speed not fast enough for the expected sampling rate")
    sys.exit(-1)
    # listv length limit check
max_number_samples_for_listv_keithley_source = 900
    # list of voltages
list_fvolt_POS = np.arange(0, vg_stop + volt_step, volt_step)
list_bvolt_POS = np.arange(vg_stop, 0 - volt_step, -volt_step)
list_fvolt_NEG = np.arange(0, vg_str - volt_step, -volt_step)
list_bvolt_NEG = np.arange(vg_str, 0 + volt_step, volt_step)
n_listv = max(len(list_fvolt_POS), len(list_bvolt_POS), len(list_fvolt_NEG), len(list_bvolt_NEG))
print(f"{len(list_fvolt_POS)=}")
print(f"{len(list_bvolt_POS)=}")
print(f"{len(list_fvolt_NEG)=}")
print(f"{len(list_bvolt_NEG)=}")
print(f"{n_listv} and {max_number_samples_for_listv_keithley_source=}")
if n_listv > max_number_samples_for_listv_keithley_source:
    print("TOO MANY SAMPLES for listv!")
    sys.exit(-1)

    # DRAIN - SMUA
vd_str = -0.3 # [V]
vd_stop = 0.1 # [V]
volt_step = 0.1 # [V]
vd_sweep= np.arange(vd_str, vd_stop + volt_step, volt_step)

# ======
# Update the parameters of the `.tsp` file same name as this python file 
# ======
logging.info("update the //.tsp// ")
print(f"{'='*5}\nupdate the //.tsp//\n{'='*5}")
file_tsp_path = r"C:\Users\20245580\LabCode\Codes_For_Experiments\codes\oect_profiling\fixed_vds_sweep_vgs_measure_ids_v3.tsp"
with open(file_tsp_path, 'r') as file:
    lines = file.readlines()

ln_idx = 11
lines[ln_idx-1]= 'startv_a = ' + str(vd_str)\
            + '\n' 

ln_idx = 12
lines[ln_idx-1]= 'stopv_a = ' + str(vd_stop)\
            + '\n'

ln_idx = 16
lines[ln_idx-1]= 'startv_b = ' + str(vg_str)\
            + '\n'

ln_idx = 17
lines[ln_idx-1]= 'stopv_b = ' + str(vg_stop)\
            + '\n'

ln_idx = 20
lines[ln_idx-1]= 'stime = ' + str(time_step)\
            + '\n'

ln_idx = 23
lines[ln_idx-1]= 'points = ' + str(len(list_fvolt_POS))\
            + '\n' 

ln_idx = 26
lines[ln_idx-1]= 'number_of_sweeps = ' + str(number_of_sweeps)\
            + '\n' 

ln_idx = 113
lines[ln_idx-1]= 'smu_drain.measure.nplc = ' + str(nplc_set)\
            + '\n' 

ln_idx = 123
lines[ln_idx-1]= 'smu_gate.measure.nplc = ' + str(nplc_set)\
            + '\n' 

    # smu.trigger.source.listv({3, 1, 4, 5, 2})
    # reference: strip of bracket of python list converted to string https://www.geeksforgeeks.org/python/python-remove-square-brackets-from-list/
ln_idx = 181
lines[ln_idx-1]= '\t'+'smu_gate.trigger.source.listv({' + str(list_fvolt_POS.tolist()).replace("[","").replace("]","") + "})"\
            + '\n'

ln_idx = 193
lines[ln_idx-1]= '\t'+'smu_gate.trigger.source.listv({' + str(list_bvolt_POS.tolist()).replace("[","").replace("]","") + "})"\
            + '\n' 

ln_idx = 206
lines[ln_idx-1]= '\t'+'smu_gate.trigger.source.listv({' + str(list_fvolt_NEG.tolist()).replace("[","").replace("]","") + "})"\
            + '\n'

ln_idx = 219
lines[ln_idx-1]= '\t'+'smu_gate.trigger.source.listv({' + str(list_bvolt_NEG.tolist()).replace("[","").replace("]","") + "})"\
            + '\n' 

    # DEBUG PURPOSE ONLY
ln_idx = 13
lines[ln_idx-1]= 'vd = ' + str(vd_str)\
            + '\n'

# Write the modified lines back to the file
with open(file_tsp_path, 'w') as file:
    file.writelines(lines)
logging.info("FINISH MODIFY //.tsp//")

# ======
# Update the parameters of the plotting file
# ======
logging.info("update the //plotting file// ")
print(f"{'='*5}\nupdate the //plotting file//\n{'='*5}")
file_plot_path = r"C:\Users\20245580\LabCode\Codes_For_Experiments\codes\oect_profiling\plot_fixed_vds_sweep_vgs_measure_ids.py"
with open(file_plot_path, 'r') as file:
    lines = file.readlines()

ln_idx = 22
lines[ln_idx-1]= 'number_of_sweeps_vds = ' + str(len(vd_sweep))\
            + '\n'

ln_idx = 24
lines[ln_idx-1]= 'len_data_per_sweep_vds = ' + str((len(list_fvolt_POS)+len(list_bvolt_POS))*number_of_sweeps)\
            + '\n'

# Write the modified lines back to the file
with open(file_plot_path, 'w') as file:
    file.writelines(lines)

logging.info("FINISH MODIFY //plotting file//")

# ======
# Keithley configure, setup tsp code
# ======
logging.info("KEITHLEY: initiate")
rm = pyvisa.ResourceManager('C:/windows/System32/visa64.dll')
keithley_ID = 'USB0::0x05E6::0x2602::4522205::INSTR'
keithley_instrument = rm.open_resource(keithley_ID)
keithley_instrument.timeout = 10000


# ======
# Prepare the record file
# ======
file_path = "C:/Users/20245580/LabCode/Codes_For_Experiments/exp_data/20260518\\oect_profiling_transfer_curve.csv"
                # ======
                # Prepare record file
                # ======
logging.info("Prepare record file")
field_names =  ['time_g', 'time', 'i_channel', 'v_drain', 'i_gate',  'v_gate', 'date_time', 'comment']
if os.path.exists(file_path):
        print("File exists.")
else:
        print("File not exist. create file")
        with open(file_path, 'a') as file:
                file_writer = csv.DictWriter(file, fieldnames=field_names)
                file_writer.writeheader()
#####
# RUN EXP, RECORD TO FILE
#####

try:
    for vds_iter in vd_sweep:
            # set gate voltage
        logging.info(f"Set drain voltage to {vds_iter} [V]")
        with open(file_tsp_path, 'r') as file:
            lines = file.readlines()
        ln_idx = 13
        lines[ln_idx-1]= 'vd = ' + str(vds_iter)\
                    + '\n'
        # Write the modified lines back to the file
        with open(file_tsp_path, 'w') as file:
            file.writelines(lines)

            # Upload the tsp scripts to keithley
        logging.info("KEITHLEY: upload codes")
        keithley_instrument.write(f"loadscript SourceRecord")
        with open(file_tsp_path) as fp:
            for line in fp: keithley_instrument.write(line)
        keithley_instrument.write("endscript")
            # run keithley program
        logging.info("SourceRecord")
        print("SourceRecord phase")
        keithley_instrument.write("SourceRecord.run()") 

        print("waiting for keithley program to complete...")
        keithley_instrument.close()

        comment_exp = input("ENTER to end (ONLY AFTER KEITHLEY PROGRAM FINISH): ")
        print("end of waiting...")
        keithley_instrument = rm.open_resource(keithley_ID)

        # record to file
        logging.info(f"Save data to file")
                    # save to file
        cur_time = 0 #time.time()
        cur_datetime = datetime.now()
        na_samples = int(float(keithley_instrument.query(f"print(smua.nvbuffer1.n)")))
        nb_samples = int(float(keithley_instrument.query(f"print(smub.nvbuffer1.n)")))
        # n_samples = 1000
        print(f"{na_samples=}")
        print(f"{nb_samples=}")
        comment_exp = ""
        for i in range(0, na_samples):
                        measured_id = float(keithley_instrument.query(f"print(smua.nvbuffer1.readings[{i}+1])"))
                        faked_ig = 0
                        keithely_time_stamp = float(keithley_instrument.query(f"print(smua.nvbuffer1.timestamps[{i}+1])"))
                        keithely_time_stamp_g = float(keithley_instrument.query(f"print(smub.nvbuffer1.timestamps[{i}+1])"))
                        measured_vd = float(keithley_instrument.query(f"print(smua.nvbuffer1.sourcevalues[{i}+1])"))
                        measured_vg = float(keithley_instrument.query(f"print(smub.nvbuffer1.readings[{i}+1])"))
                        with open(file_path, 'a') as file: 
                                            # NOTICE: THE WHILE LOOP/ FOR LOOP INSIDE -> NO CONSTANT UPDATE TO FILE AT ALL -> NO ANIMATION
                            file_writer = csv.DictWriter(file, fieldnames=field_names)
                            info = {
                                    'time_g': cur_time + keithely_time_stamp_g,
                                    'time':cur_time + keithely_time_stamp,
                                    'i_channel': measured_id,
                                    'v_drain': measured_vd,
                                    'i_gate': faked_ig,
                                    'v_gate': measured_vg,
                                    'date_time': cur_datetime,
                                    'comment': comment_exp + 'unit [V], [s]'
                                                + '- scan rate ' + str(scan_rate) + ' [V/s]'
                                                + 'time step ' + str(time_step) + ' [s]'
                                                + '- no measurement of gate current, gate voltage is the set value',

                                    }
                            file_writer.writerow(info)

        logging.info(f"Program end successfully")

except Exception as e:
      
    sys.exit(-1)
    logging.info(f"EXIT WITH ERROR")



