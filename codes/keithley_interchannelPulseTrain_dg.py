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
from  keithley2600 import Keithley2600
import time
import logging
import pyfirmata
import csv
import os
from datetime import datetime

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
        # Keithley, smua drain for read
        # ======
rm = pyvisa.ResourceManager('C:/windows/System32/visa64.dll')
keithley_instrument = rm.open_resource('USB0::0x05E6::0x2636::4480001::INSTR')
keithley_instrument.timeout = 10000
        # configure
keithley_instrument.write(f"smua.measure.nplc = 1")

        # ======
        # Upload the keithley scripts to keithley for the program
        # ======
# script for writing phase
file_tsp_path = "C:\\Users\\20245580\\LabCode\\Codes_For_Experiments\\codes\\pulse_train_2ch_dg.tsp" 
keithley_instrument.write(f"loadscript Write")
with open(file_tsp_path) as fp:
    for line in fp: keithley_instrument.write(line)
keithley_instrument.write("endscript") 

# script for reading phase
file_tsp_path = "C:\\Users\\20245580\\LabCode\\Codes_For_Experiments\\codes\\single_pulse_measurement.tsp" 
keithley_instrument.write(f"loadscript Read")
with open(file_tsp_path) as fp:
    for line in fp: keithley_instrument.write(line)
keithley_instrument.write("endscript") 

# SMUA (drain parameters, extract from `pulse_train_2ch.tsp`)
vd_amplitude = 0.8 #0.05 # pulse_volt # [V]
vg_amp = 0.01
bias_volt = 0 # [V], positve zero; if pulse negative, set to negative zero


pulse_period = 0.5 # [s]
pulse_width = 0.1 # [s]
delta_tpre_tpost = 0.05 # [s]
n_write_cycle = 3



write_func_complete = delta_tpre_tpost + n_write_cycle*pulse_period

        # read pulse
read_pulse_on = 0.5
read_pulse_off = 1
number_read_pulses = 3
read_func_complete = (read_pulse_on + read_pulse_off)*number_read_pulses

        # # ======
        # # record to file
        # # ======
file_path = "C:/Users/20245580/LabCode/Codes_For_Experiments/exp_data/20250911/pulse_exp.csv"
file_path_avg = "C:/Users/20245580/LabCode/Codes_For_Experiments/exp_data/20250911/pulse_exp_avg.csv"
                # ======
                # Prepare record file
                # ======
logging.info("Prepare record file")
field_names = ['time', 'i_channel', 'date_time', 'comment']
if os.path.exists(file_path):
        print("File exists.")
else:
        print("File not exist. create file")
        with open(file_path, 'a') as file:
                file_writer = csv.DictWriter(file, fieldnames=field_names)
                file_writer.writeheader()


field_names_avg = ['time', 'i_channel_avg', 'date_time', 'comment']
if os.path.exists(file_path_avg):
        print("File exists.")
else:
        print("File not exist. create file")
        with open(file_path_avg, 'a') as file:
                file_writer = csv.DictWriter(file, fieldnames=field_names_avg)
                file_writer.writeheader()


        # ======
        # start measurement
        # ======
logging.info("start measurement")
time_ref = time.time()

logging.info("comment about the exp")
comment_exp = input("comment about exp (dg or gd): ")

try:
    # for n_exp
    nexp = 100
    sw_settle_time = 1 # [s]
    wait_between_read_and_write = 5 # [s]
    wait_between_exp = 5 # [s] = wait between write and read

    # wait for initial conds stable
    time.sleep(5)
    
    for idx_exp in range(0, nexp):

        # time.sleep(wait_between_read_and_write)
        logging.info("writing phase")
        print("writing phase")
        keithley_instrument.write("Write.run()") 

        time.sleep(write_func_complete)
        
        logging.info("writing successfully")

        time.sleep(wait_between_read_and_write)
        
        # read
        logging.info("reading phase")
        print("read phase")
        try:
            keithley_instrument.write("Read.run()")

            time.sleep(read_func_complete)

            logging.info(f"read successfully")
            # save to file
            cur_time = time.time()
            cur_datetime = datetime.now()
            n_samples = int(float(keithley_instrument.query(f"print(smua.nvbuffer1.n)")))
            average = 0
            for i in range(0, n_samples):
                measured_i = float(keithley_instrument.query(f"print(smua.nvbuffer1.readings[{i}+1])"))
                keithely_time_stamp = float(keithley_instrument.query(f"print(smua.nvbuffer1.timestamps[{i}+1])"))
                measured_vd = float(keithley_instrument.query(f"print(smua.nvbuffer1.sourcevalues[{i}+1])"))
                with open(file_path, 'a') as file: 
                                    # NOTICE: THE WHILE LOOP/ FOR LOOP INSIDE -> NO CONSTANT UPDATE TO FILE AT ALL -> NO ANIMATION
                    file_writer = csv.DictWriter(file, fieldnames=field_names)
                    info = {
                            'time':cur_time - time_ref + keithely_time_stamp,
                            'i_channel': measured_i,
                            'date_time': cur_datetime,
                            'comment': comment_exp + '; vg: [V]' + str(vg_amp) 
                                        + '; vd: [V]'+ str(vd_amplitude) 
                                        + '; read_pulse: [V]'+ str(measured_vd)
                                        + '; delta_t: [s]' + str(delta_tpre_tpost)
                                        + '; pulse_width [s]: ' + str(pulse_width)
                                        + '; pulse_period [s]: ' + str(pulse_period)
                                        + '; n_read_points: ' + str(n_samples)
                                        + '; n_write_cycle : ' + str(n_write_cycle)
                                        + '; sw_settle_time [s]: ' + str(sw_settle_time)
                                        + '; wait_between_read_and_write [s]: ' + str(wait_between_read_and_write)
                                        + '; wait_between_exp [s]: ' + str(wait_between_exp),

                            }
                    file_writer.writerow(info)
                average = average + measured_i
            average = average/ n_samples
            with open(file_path_avg, 'a') as file: 
                    # NOTICE: THE WHILE LOOP/ FOR LOOP INSIDE -> NO CONSTANT UPDATE TO FILE AT ALL -> NO ANIMATION
                file_writer = csv.DictWriter(file, fieldnames=field_names_avg)
                info = {
                        'time':cur_time - time_ref,
                        'i_channel_avg': average,
                        'date_time': cur_datetime,
                        'comment': comment_exp + '; vg: [V]' + str(vg_amp) 
                                        + '; vd: [V]'+ str(vd_amplitude) 
                                        + '; read_pulse: [V]'+ str(measured_vd)
                                        + '; delta_t: [s]' + str(delta_tpre_tpost)
                                        + '; pulse_width [s]: ' + str(pulse_width)
                                        + '; pulse_period [s]: ' + str(pulse_period)
                                        + '; n_read_points: ' + str(n_samples)
                                        + '; n_write_cycle : ' + str(n_write_cycle)
                                        + '; sw_settle_time [s]: ' + str(sw_settle_time)
                                        + '; wait_between_read_and_write [s]: ' + str(wait_between_read_and_write)
                                        + '; wait_between_exp [s]: ' + str(wait_between_exp),
                        }
                file_writer.writerow(info)
            
            # clear keithley buffer before another read
        #     keithley_instrument.smua.source.output = keithley_instrument.smua.OUTPUT_ON  
        #     time.sleep(keithley_settle_time)

        except Exception as e:
            logging.info(f"Keithley error: {e=}")
            logging.info(f"EXIT: {e=}")
            sys.exit(-1)

        # wait between exp
        time.sleep(wait_between_exp)

    logging.info("MEASUREMENT FINISH")
    
except KeyboardInterrupt:
    print(f"MEASUREMENT: EXIT KeyboardInterrupt")
    keithley_instrument.write(f"smua.source.output = smua.OUTPUT_OFF")
    keithley_instrument.write(f"smub.source.output = smub.OUTPUT_OFF")

