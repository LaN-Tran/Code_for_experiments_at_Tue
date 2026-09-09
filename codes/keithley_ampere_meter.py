"""
    Automation Keithley 2602B, 2602A measurement
    Ampere meter
    Author:  Tran Le Phuong Lan.
    Created:  2026-09-08

    Requires:
       NI VISA - NI MAX                        
       Python 2.7, 3
       pyvisa
    Reference:

"""

# Libs
import pyvisa
import time
from  keithley2600 import Keithley2600, ResultTable
import threading
import logging
import pyfirmata
import time
import json
import numpy as np
import os
import matplotlib.pyplot as plt
import multiprocessing, time, signal
import csv
import pandas as pd
import matplotlib.animation as animation

# check the instrument (e.g Keithley 2602B) VISA address
# rm = pyvisa.ResourceManager('C:/windows/System32/visa64.dll')
# print(rm.list_resources())


# init logger
format = "%(asctime)s: %(message)s"
log_file_path = 'example.log'
logging.basicConfig(format=format, level=logging.INFO,  
                        datefmt="%H:%M:%S", filename= log_file_path, filemode= 'w')

        # init the instrument handle
    # k = Keithley2600('USB0::0x05E6::0x2636::4480001::INSTR', visa_library = 'C:/windows/System32/visa64.dll')
# keithley_instrument = Keithley2600('USB0::0x05E6::0x2636::4480001::INSTR', visa_library = 'C:/windows/System32/visa64.dll')
rm = pyvisa.ResourceManager('C:/windows/System32/visa64.dll')
keithley_id = 'TCPIP0::192.109.209.11::inst0::INSTR'
keithley_instrument = rm.open_resource(keithley_id)
keithley_instrument.timeout = 10000
        # Turn everything OFF
keithley_instrument.write('smua.source.output = smua.OUTPUT_OFF')   # turn off SMUA
keithley_instrument.write('smub.source.output = smub.OUTPUT_OFF')   # turn off SMUB
time.sleep(1)


        # path to the measurement record
file_path = "C:/Users/20245580/LabCode/Codes_For_Experiments/exp_data/20260408/ecram.csv"

logging.info("Main    : Prepare measurement")

sw_settle_time = 0.1 # [s]
# gate_bias_voltage = 0.2 #[s]
gate_bias_voltage_p1 = 0 #[V]
gate_bias_voltage_p2 = 0 #[V]
gate_bias_voltage_measure = 0.1 #[V]
drain_bias_voltage = 0.05 # [V]
keithley_settle_time = 0.1 # [s]
wait_before_exp = 60 # [s]
nexp = 20
series_pulses = 2 # 2 pulses for each n_pulse_type_1 or n_pulse_type_2 cycle
n_pulse_type_1 = 4
# there is an outer loop for this, to change the amplitude after each exp
step_voltage = 0
amp_pulse_type_1 = 1 # (Vgs > 0, decrease gm. bcz source is always 0, and drain - source are symmertrical)
pulse_width_type_1 = 2
pulse_period_type_1 = 6
no_pulse_time_type_1 = pulse_period_type_1 - pulse_width_type_1
wait_between_pulse_type_1 = 300 # In this case, we reuse as measurement period for 2 terminal memristor
wait_between_pulse_type_1_and_pulse_type_2 = 1 
n_pulse_type_2 = 4
amp_pulse_type_2 = -1 # (Vgs < 0, increase gm.  bcz source is always 0, and drain - source are symmertrical)
pulse_width_type_2 = 2
pulse_period_type_2 = 6
no_pulse_time_type_2 = pulse_period_type_2 - pulse_width_type_2
wait_between_pulse_type_2 = 300 # In this case, we reuse as measurement period for 2 terminal memristor
wait_between_exp = 1

try:
    
                # ======
                # Prepare record file
                # ======
    field_names = ['time', 'i_channel', 'v_drain','i_gate', 'v_gate']
    with open(file_path, 'w') as file:
        file_writer = csv.DictWriter(file, fieldnames=field_names)
        file_writer.writeheader()

    # ======
    # KEITHLEY FOR VOLTMETER ONLY
    # ======
    lowest_source_range_v = 100e-3 # V
    compliance_limit_i = 100e-3 # A
    rangei = 10e-3 # A
        # ======
        # Configure smub as amperemeter
        # ======
                # assign the smub to smu_amp
    keithley_instrument.write('smu_amp = smub')  
                # reset the channel          
    keithley_instrument.write('smu_amp.reset()')
                # Clear buffer 1.
    keithley_instrument.write('smu_amp.nvbuffer1.clear()')
                # Select the volt source function.
    keithley_instrument.write('smu_amp.source.func = smu_amp.OUTPUT_DCVOLTS')
                # Set the source level to 0.
    keithley_instrument.write(f"smu_amp.source.levelv = {0}")
                # Select lowest source range
    keithley_instrument.write(f"smu_amp.source.rangev = {lowest_source_range_v}")
                # MUST set the compliance limit > expected measured
    keithley_instrument.write(f"smu_amp.source.limiti = {compliance_limit_i}")
                # set the RANGE for measurement range
    keithley_instrument.write(f"smu_amp.source.autorangei = smu_amp.AUTORANGE_OFF ")
    keithley_instrument.write(f"smu_amp.source.rangei = {rangei}")
    keithley_instrument.write(f"smu_amp.measure.autozero = smu_amp.AUTOZERO_AUTO")
                    
   
                    
                # # ======
                # # Turn on Keithley
                # # ======
    logging.info("Turn on Keithley")
    keithley_instrument.write('smu_amp.source.output = smu_amp.OUTPUT_ON')  
    time.sleep(keithley_settle_time)

    logging.info("start measurement")
    time_ref = time.time()
    
    # before exp
    logging.info("before exp")
    start_time = time.time()
    current_time = time.time()
    while (current_time - start_time) < wait_before_exp:
        try:
            measured_i_channel = 0
            measured_v_drain = 0
            measured_i_gate =  float(keithley_instrument.query('print(smu_amp.measure.i())'))
            measured_v_gate = 0
            # record to file
            with open(file_path, 'a') as file: 
                        # NOTICE: THE WHILE LOOP/ FOR LOOP INSIDE -> NO CONSTANT UPDATE TO FILE AT ALL -> NO ANIMATION
                file_writer = csv.DictWriter(file, fieldnames=field_names)
                info = {
                        'time': time.time() - time_ref,
                        'i_channel': measured_i_channel,
                        'v_drain': measured_v_drain,
                        'i_gate': measured_i_gate,
                        'v_gate': measured_v_gate,
                                                    }
                file_writer.writerow(info)
        
        except Exception as CatchError:
            logging.info("ERROR: keithley measure function error")
            logging.info(f"{CatchError=}")

        current_time = time.time()

    # end exp
    logging.info("Keithley measurement    : EXIT")
            # turn off the keithley
    keithley_instrument.write('smu_amp.source.output = smu_amp.OUTPUT_OFF')   # turn off SMU AMP

except KeyboardInterrupt:
        # # ======
        # # Open all switches
        # # ======
    logging.info("Keithley measurement    : EXIT")
            # turn off the keithley
    keithley_instrument.write('smub.source.output = smub.OUTPUT_OFF')   # turn off SMUB
