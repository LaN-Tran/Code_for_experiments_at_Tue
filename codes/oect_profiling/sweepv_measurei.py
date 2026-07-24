# generate the the voltage sweep list
"""
    Automation Keithley 2602B
    SWEEP V, MEASURE I
    Reuse the plot python script of : sweep vds, measure ids, fixed gds
    Author:  Tran Le Phuong Lan.
    Created:  2026-07-21

    Requires:                       
       Python 2.7, 3
       pyvisa
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
    # DRAIN - SMUA
number_of_sweeps = 5
scan_rate = 0.05 # [V/s] # 0.1 = the min scan rate
sampling_speed = 100 # 10e+3 # [Hz] (max 50kHz, depends on keithley)
time_step = 1/sampling_speed
volt_step = (time_step * scan_rate)
Vd_step_offset = volt_step / 10
volt_step = (time_step * scan_rate) + Vd_step_offset
# `Vd_neg` MUST < `Vd_stop`, otherwise cause error in list generation `list_fvotl_neg`, `list_bvotl_neg` below
Vd_neg = -0.8 # [V]
Vd_pos = 0.8 # [V] 
Vd_stop = 0 # [V]
Vd_abs_max = max(abs(Vd_neg), abs(Vd_pos))
    # time step limit check
nplc_set = 0.1 # 0.01/2 # (1 = 1/50Hz = )
print(f"{nplc_set * (1/50)=} and {time_step=}")
if nplc_set * (1/50) > time_step:
    print("A/D speed not fast enough for the expected sampling rate")
    sys.exit(-1)
    # listv length limit check
max_number_samples_for_listv_keithley_source = 900
    # list of voltages
list_start = np.arange(0, Vd_pos, volt_step)
list_bvotl = np.arange(Vd_pos, Vd_neg, -volt_step)
list_bvotl_1 = list_bvotl[0:int(len(list_bvotl)/2)]
list_bvotl_2 = list_bvotl[int(len(list_bvotl)/2):] 
list_fvotl = np.arange(Vd_neg, Vd_pos, volt_step)
list_fvotl_1 = list_fvotl[0:int(len(list_fvotl)/2)]
list_fvotl_2 = list_fvotl[int(len(list_fvotl)/2):]
list_end = np.arange(Vd_pos, 0-volt_step, -volt_step)
n_listv = max(len(list_fvotl_1), len(list_fvotl_2),
              len(list_bvotl_1), len(list_bvotl_2),
              len(list_start), 
              len(list_end))
print(f"{len(list_fvotl_1)=}")
print(f"{len(list_fvotl_2)=}")
print(f"{len(list_bvotl_1)=}")
print(f"{len(list_bvotl_2)=}")
print(f"{len(list_start)=}")
print(f"{len(list_end)=}")
print(f"{n_listv} and {max_number_samples_for_listv_keithley_source=}")
# if n_listv > max_number_samples_for_listv_keithley_source:
#     print("TOO MANY SAMPLES for listv!")
#     sys.exit(-1)

    # GATE - SMUB (DOES NOT MATTER IN THIS MEASUREMENT, BUT MUST BE SET TO A FIXED VALUE)
vg_str = -0.1 # [V]
vg_stop = -0.1 # [V]
volt_step = 0.1 # [V]
vg_sweep= np.arange(vg_str, vg_stop + volt_step, volt_step)

# ======
# Update the parameters of the `.tsp` file same name as this python file 
# ======
logging.info("update the //.tsp// ")
print(f"{'='*5}\nupdate the //.tsp//\n{'='*5}")
file_tsp_path = r"C:\Users\20245580\LabCode\Codes_For_Experiments\codes\oect_profiling\sweepv_measurei.tsp"
with open(file_tsp_path, 'r') as file:
    lines = file.readlines()

ln_idx = 13
lines[ln_idx-1]= 'start_vd = ' + str(Vd_abs_max)\
            + '\n' 

ln_idx = 14
lines[ln_idx-1]= 'stop_vd = ' + str(Vd_stop)\
            + '\n'

ln_idx = 16
lines[ln_idx-1]= 'stime = ' + str(time_step)\
            + '\n'

ln_idx = 18
lines[ln_idx-1]= 'points_str = ' + str(len(list_start))\
            + '\n'

ln_idx = 22
lines[ln_idx-1]= 'number_of_sweeps = ' + str(number_of_sweeps)\
            + '\n'

ln_idx = 63
lines[ln_idx-1]= 'smu_drain.measure.nplc = ' + str(nplc_set)\
            + '\n' 

    # smu.trigger.source.listv({3, 1, 4, 5, 2})
    # reference: strip of bracket of python list converted to string https://www.geeksforgeeks.org/python/python-remove-square-brackets-from-list/
ln_idx = 87
lines[ln_idx-1]= 'volt_offset = ' + str(Vd_step_offset)\
            + '\n'
# ln_idx = 89
# lines[ln_idx-1]= 'smu_drain.trigger.source.listv({' + str(list_start.tolist()).replace("[","").replace("]","") + "})"\
#             + '\n' 

ln_idx = 98
lines[ln_idx-1]= 'points_bw_1 = ' + str(len(list_bvotl_1))\
            + '\n'
# ln_idx = 104
# lines[ln_idx-1]= '\t'+'smu_drain.trigger.source.listv({' + str(list_bvotl_1.tolist()).replace("[","").replace("]","") + "})"\
#             + '\n'

ln_idx = 106
lines[ln_idx-1]= 'points_bw_2 = ' + str(len(list_bvotl_2))\
            + '\n'
# ln_idx = 110
# lines[ln_idx-1]= '\t'+'smu_drain.trigger.source.listv({' + str(list_bvotl_2.tolist()).replace("[","").replace("]","") + "})"\
#             + '\n'

ln_idx = 114
lines[ln_idx-1]= 'points_fw_1 = ' + str(len(list_fvotl_1))\
            + '\n'
# ln_idx = 124
# lines[ln_idx-1]= '\t'+'smu_drain.trigger.source.listv({' + str(list_fvotl_1.tolist()).replace("[","").replace("]","") + "})"\
#             + '\n'

ln_idx = 122
lines[ln_idx-1]= 'points_fw_2 = ' + str(len(list_fvotl_2))\
            + '\n'
# ln_idx = 131
# lines[ln_idx-1]= '\t'+'smu_drain.trigger.source.listv({' + str(list_fvotl_2.tolist()).replace("[","").replace("]","") + "})"\
#             + '\n' 

ln_idx = 130
lines[ln_idx-1]= 'points_end = ' + str(len(list_end))\
            + '\n'
# ln_idx = 148
# lines[ln_idx-1]= 'smu_drain.trigger.source.listv({' + str(list_end.tolist()).replace("[","").replace("]","") + "})"\
#             + '\n' 

    # DEBUG PURPOSE ONLY
# ln_idx = 20
# lines[ln_idx-1]= 'vgs = ' + str(vg_sweep[0])\
#             + '\n'

# Write the modified lines back to the file
with open(file_tsp_path, 'w') as file:
    file.writelines(lines)
logging.info("FINISH MODIFY //.tsp//")

# ======
# Update the parameters of the plotting file
# ======
logging.info("update the //plotting file// ")
print(f"{'='*5}\nupdate the //plotting file//\n{'='*5}")
file_plot_path = r"C:\Users\20245580\LabCode\Codes_For_Experiments\codes\oect_profiling\plot_fixed_vgs_sweep_vds_measure_ids.py"
with open(file_plot_path, 'r') as file:
    lines = file.readlines()

ln_idx = 22
lines[ln_idx-1]= 'number_of_sweeps_vgs = ' + str(len(vg_sweep))\
            + '\n'

ln_idx = 24
lines[ln_idx-1]= 'len_data_per_sweep_vgs = ' + str((len(list_fvotl_1)+len(list_fvotl_2)+len(list_bvotl_1)+len(list_bvotl_2))*number_of_sweeps 
                                                   + len(list_end) 
                                                   + len(list_start))\
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
keithley_ID = 'USB0::0x05E6::0x2636::4480001::INSTR'
keithley_instrument = rm.open_resource(keithley_ID)
keithley_instrument.timeout = 10000


# ======
# Prepare the record file
# ======
file_path = "C:/Users/20245580/LabCode/Codes_For_Experiments/exp_data/20260518\\oect_profiling_output_curve.csv"
                # ======
                # Prepare record file
                # ======
logging.info("Prepare record file")
field_names =  ['time', 'i_channel', 'i_gate', 'v_drain', 'v_gate', 'date_time', 'comment']
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
    for vgs_iter in vg_sweep:
            # set gate voltage
        logging.info(f"Set gate voltage to {vgs_iter} [V]")
        with open(file_tsp_path, 'r') as file:
            lines = file.readlines()
        ln_idx = 20
        lines[ln_idx-1]= 'vgs = ' + str(vgs_iter)\
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
        n_samples = int(float(keithley_instrument.query(f"print(smua.nvbuffer1.n)")))
        # n_samples = 1000
        print(f"{n_samples=}")
        comment_exp = ""
        for i in range(0, n_samples):
                        measured_i = float(keithley_instrument.query(f"print(smua.nvbuffer1.readings[{i}+1])"))
                        keithely_time_stamp = float(keithley_instrument.query(f"print(smua.nvbuffer1.timestamps[{i}+1])"))
                        measured_vd = float(keithley_instrument.query(f"print(smua.nvbuffer1.sourcevalues[{i}+1])"))
                        faked_igs = 0
                        faked_vgs = vgs_iter
                        with open(file_path, 'a') as file: 
                                            # NOTICE: THE WHILE LOOP/ FOR LOOP INSIDE -> NO CONSTANT UPDATE TO FILE AT ALL -> NO ANIMATION
                            file_writer = csv.DictWriter(file, fieldnames=field_names)
                            info = {
                                    'time':cur_time + keithely_time_stamp,
                                    'i_channel': measured_i,
                                    'i_gate': faked_igs,
                                    'v_drain': measured_vd,
                                    'v_gate': faked_vgs,
                                    'date_time': cur_datetime,
                                    'comment': comment_exp + 'unit [V], [s]'
                                                + '- scan rate: ' + str(scan_rate) + ' [V/s]'
                                                + '- time step: ' + str(time_step) + ' [s]'
                                                + '- no measurement of gate current, gate voltage is the set value',

                                    }
                            file_writer.writerow(info)

        logging.info(f"Program end successfully")

except Exception as e:
      
    sys.exit(-1)
    logging.info(f"EXIT WITH ERROR")



