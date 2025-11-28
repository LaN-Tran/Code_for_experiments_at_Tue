"""
    Automation Keithley 2602B, AD3
    Keithley 2636B - LAN, Oscilloscope Rigol DS1054
    Author:  Tran Le Phuong Lan.
    Created:  2025-11-28

    Requires:                       
       Python 2.7, 3
       pyvisa
       Keithley2600
    Reference:
        [1] https://github.com/LaN-Tran/Automate_Lab_Instrument/tree/main/20250905
"""

import pyvisa
import time
import logging
# import pyfirmata
import csv
import os
from datetime import datetime
import numpy as np

# Initialization
    # # ======
    # # Logger
    # # ======
# init logger
format = "%(asctime)s: %(message)s"
log_file_path = 'example.log'
logging.basicConfig(format=format, level=logging.INFO,  
                        datefmt="%H:%M:%S", filename= log_file_path, filemode= 'w')

        # open resource manager for both keithley and osc
rm = pyvisa.ResourceManager('C:/windows/System32/visa64.dll')
        # ======
        # Keithley, smua drain for read
        # ======
keithley_instrument = rm.open_resource('USB0::0x05E6::0x2636::4480001::INSTR')
keithley_instrument.timeout = 10000
logging.info(f"KEITHLEY: connect successfully")

        # ======
        # Upload the keithley scripts to keithley for the program
        # ======
    # script for writing phase
file_tsp_path = "C:/Users/20245580/LabCode/Codes_For_Experiments/codes\\pulse_train_2ch_dg.tsp" 
keithley_instrument.write(f"loadscript Write")
with open(file_tsp_path) as fp:
    for line in fp: keithley_instrument.write(line)
keithley_instrument.write("endscript")
logging.info(f"KEITHLEY: upload keithley pulse code successfully")

    # parameter
vd_amplitude = 2.5 # pulse_volt # [V]
pulse_period = 0.01  # [s]
pulse_width = 0.001 # [s]
delta_tpre_tpost = 0.05 # [s]
n_write_cycle = 10
write_func_complete = delta_tpre_tpost + n_write_cycle*pulse_period

wait_between_read_and_write = 2 
wait_osc_setup_keithley_run = 5
        # ======
        # Oscilloscope
        # ======
logging.info(f"OSC: setup starts")
osc_rig = rm.open_resource('USB0::0x1AB1::0x04CE::DS1ZA221403528::INSTR')
logging.info(f"OSC: connect successfully")
    # [1], `./README.md`
osc_rig.timeout = 1500 # [ms]
osc_rig.chunk_size = 32 
max_points = 250_000

    # set the waveform mode to RAW to read the data from the internal memory instead
osc_rig.write(':WAV:MODE RAW')
    # set the waveform format
osc_rig.write(':WAV:FORM BYTE') 
    # check the setup
logging.info(f"OSC: {osc_rig.query(':WAV:MODE?')=}")
logging.info(f"OSC: {osc_rig.query(':WAV:FORM?')=}")

    # if the source where the data will be collected is not as wanted,
    # configure as
osc_rig.write(':WAV:SOUR CHAN2')
logging.info(f"OSC: {osc_rig.query(':WAV:SOUR?')}")

    # Manual: the Rigol ds1054 - button `ACQUIRE` - button `Mem Depth`
    # The valid memory depth values are
    # 6K
    # 60K
    # 600K
    # 6M
    # 12M

    # IMPORTANT:
    # The osc memory depth can only be set/ configured when the osc is in `RUN` state. 
    # If the osc is in `STOP` state, we can only query the memory depth
    # Query the memory depth of the internal memory osc is possible in both cases.
internal_mem_osc_total_points = 6_000_000
osc_rig.write(':ACQ:MDEP '+str(internal_mem_osc_total_points))
# check the current internal memory depth
mem_depth = osc_rig.query(':ACQ:MDEP?')
mem_depth = int(mem_depth)
logging.info(f"OSC: {mem_depth=}")

        # # ======
        # # record to file
        # # ======
file_path = "C:/Users/20245580/LabCode/Codes_For_Experiments/exp_data/20251126\\neuron_mem.csv"
logging.info("Prepare record file")
field_names = ['time', 'volts']
with open(file_path, 'w') as file:
                file_writer = csv.DictWriter(file, fieldnames=field_names)
                file_writer.writeheader()

# start keithley pulse
    # start the oscilloscope first
osc_rig.write(':RUN')
logging.info("OSC: RUN")
# set single capture
osc_rig.write(':SING')
logging.info("OSC: set SINGLE capture mode")

time.sleep(wait_osc_setup_keithley_run)

    # start the keithley
logging.info("Keithley: writing phase")
print("writing phase STARTS")

keithley_instrument.write("Write.run()") 
time.sleep(write_func_complete)

logging.info("Keithley: writing successfully")
time.sleep(wait_between_read_and_write)

print("writing phase DONE")


# transfer data from oscilloscope
    # since each time we can not read more than 250000 samples with :WAV:DATA? (because the WAV:FORM BYTE is already set),
    # we need to read in batches. To make sure that the next index inside of the internal buffer is surely known, 
    # we set the number of sample to be read < 250000 samples. 
    # The index in the internal memory oscilloscope starts from 1.
    # If there are N points in the memory, the index starts from 1 to N.

    # prefer to choose `samples_in_a_batch` is divisible by the available memory depth,
    # and < 250000. 
samples_in_a_batch = 100000 
logging.info(mem_depth/samples_in_a_batch)
number_of_batches = int(mem_depth/samples_in_a_batch)
logging.info(f"{number_of_batches=}")

buf = []
n_retries = 10
n_traces = 1

for trace in range(n_traces): # = number of time we want to run the SINGLE mode in the osc
        # set single capture
    # osc_rig.write(':SING')
    time.sleep(0.3) # wait for osc transition from RUN -> SINGLE

    # query the trigger state in osc
    while True:
        trigger_sts = osc_rig.query(':TRIG:STAT?')
        # print(f"{trigger_sts=}")
        if 'STOP' in trigger_sts:
            logging.info(f"OSC: {trigger_sts=}")
            break 
        logging.info(f"OSC: {trigger_sts=}")

        time.sleep(0.1) # if the trigger is still waiting, then we wait a bit until the next read
    
    
    # if trigger is stopped, collect the data from the internal memory
    idx_batch = 0
    len_buf = len(buf)
    while len_buf < mem_depth:
        logging.info(f"OSC: read {idx_batch=}")

        start= idx_batch*samples_in_a_batch + 1
        stop = start + samples_in_a_batch - 1
        stop = mem_depth if stop > mem_depth else stop

        time.sleep(0.01)
        osc_rig.write(f':WAV:STAR {start}')
        osc_rig.write(f':WAV:STOP {stop}')

        for i_retry in range(0, n_retries):
            try:
                tmp = osc_rig.query_binary_values(':WAV:DATA?', datatype='B')
                break
            except Exception as e:
                print(f"{e=}")

        buf += tmp

        len_buf = len(buf)
        # print(f"{len_buf=}") 
        idx_batch = idx_batch + 1

logging.info(f"OSC: read from OSC successfully")
# convert values to display the right value 
# and plot

# X-axis conversion
sampling_rate = osc_rig.query(':ACQ:SRATE?') # samples/second or points/second
sampling_rate = float(sampling_rate)
logging.info(f"OSC: {sampling_rate=}")

time_axis = np.arange(0, len(buf)) / sampling_rate

# Y-axis conversion
yorigin = osc_rig.query(':WAV:YORigin?')
yorigin = float(yorigin)
logging.info(f"OSC: {yorigin=}")

yref = osc_rig.query(':WAV:YREFerence?')
yref = float(yref)
logging.info(f"OSC: {yref=}")

yincr = osc_rig.query(':WAV:YINCrement?')
yincr = float(yincr)
logging.info(f"OSC: {yincr=}")

np_buf = np.array(buf) 
volt_axis = (np_buf - yorigin - yref)*yincr

# save to file
logging.info(f"OSC: Save to file")

with open(file_path, 'a') as file: 
                        # NOTICE: THE WHILE LOOP/ FOR LOOP INSIDE -> NO CONSTANT UPDATE TO FILE AT ALL -> NO ANIMATION
                file_writer = csv.DictWriter(file, fieldnames=field_names)
                for i in range(0, len(time_axis)):
                        info = {
                                'time': time_axis[i],
                                'volts': volt_axis[i]
                                        # 'i_gate': measured_i_gate,
                                                        }
                        
                        file_writer.writerow(info)
logging.info(f"OSC: Save to file SUC")