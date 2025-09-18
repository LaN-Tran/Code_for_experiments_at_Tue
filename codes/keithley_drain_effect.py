"""
    Automation Keithley 2602B measurement
    Drain effect experiment
    Author:  Tran Le Phuong Lan.
    Created:  2025-08-06

    Requires:                       
       Python 2.7, 3
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
keithley_instrument = Keithley2600('USB0::0x05E6::0x2636::4480001::INSTR', visa_library = 'C:/windows/System32/visa64.dll')
        # Turn everything OFF
keithley_instrument.smua.source.output = keithley_instrument.smua.OUTPUT_OFF   # turn off SMUA
keithley_instrument.smub.source.output = keithley_instrument.smub.OUTPUT_OFF   # turn off SMUB
time.sleep(1)


        # path to the measurement record
file_path = "C:/Users/20245580/LabCode/Codes_For_Experiments/exp_data/20250807/drain_effect.csv"

logging.info("Main    : Prepare measurement")

settle_time = 1 # s # after the smu configuration
    
sw_settle_time = 10e-3 # s
rest_duration = 0.2 # s

drain_voltage = 0.8 # V
try:
                # ======
                # Prepare record file
                # ======
    field_names = ['time', 'i_channel', 'v_drain']
    with open(file_path, 'w') as file:
        file_writer = csv.DictWriter(file, fieldnames=field_names)
        file_writer.writeheader()

                # ======
                # Configure smub as voltage source (Gate)
                # ======
                    # reset the channel
    keithley_instrument.smub.reset()
                
                # Clear buffer 1.
    keithley_instrument.smub.nvbuffer1.clear()

                    # Select measure I autorange.
    keithley_instrument.smub.measure.autorangei = keithley_instrument.smub.AUTORANGE_ON

                    # Select the voltage source function.
    keithley_instrument.smub.source.func = keithley_instrument.smub.OUTPUT_DCVOLTS
                    
                    # Set the bias voltage.
    keithley_instrument.smub.source.levelv = 1

                    # Select measure I autorange.
    keithley_instrument.smub.measure.autozero = keithley_instrument.smub.AUTOZERO_OFF
    keithley_instrument.smub.measure.autorangei = keithley_instrument.smub.AUTORANGE_ON
                    

                # # ======
                # # Configure smua as source v, measure i (Drain)
                # # ======

                    # Restore 2600B defaults.
    keithley_instrument.smua.reset()

                    # Select channel A display.
    keithley_instrument.display.screen = keithley_instrument.display.SMUA

                    # Display current.
    keithley_instrument.display.smua.measure.func = keithley_instrument.display.MEASURE_DCAMPS

                    # Select measure I autorange.
    keithley_instrument.smua.measure.autozero = keithley_instrument.smua.AUTOZERO_OFF
    keithley_instrument.smua.measure.autorangei = keithley_instrument.smua.AUTORANGE_ON

                    # Select ASCII data format.
                # smu.write('format.data = format.ASCII')

                    # Clear buffer 1.
    keithley_instrument.smua.nvbuffer1.clear()

                    # Select the source voltage function.
    keithley_instrument.smua.source.func = keithley_instrument.smua.OUTPUT_DCVOLTS

                    # Set the bias voltage.
    keithley_instrument.smua.source.levelv = drain_voltage

                # # ======
                # # Measuring
                # # ======

    #                 # Turn on the gate source.
    # keithley_instrument.smub.source.output = keithley_instrument.smub.OUTPUT_ON

                    # Turn on the drain source.
    keithley_instrument.smua.source.output = keithley_instrument.smua.OUTPUT_ON

                    # Settling time
    time.sleep(settle_time)


    logging.info(f"starting the measurement process")
                    # start the measurement reference time
    start_time = time.time()
                    # start measurement
    while(1):
             
            with open(file_path, 'a') as file: 
                        # NOTICE: THE WHILE LOOP/ FOR LOOP INSIDE -> NO CONSTANT UPDATE TO FILE AT ALL -> NO ANIMATION
                file_writer = csv.DictWriter(file, fieldnames=field_names)
                            
                                # set the voltage (gate)
                logging.info(f"set drain voltage {drain_voltage=}")
                
                time.sleep(settle_time)
                try:
                    measured_i_channel = keithley_instrument.smua.measure.i()
                    measured_v_drain = keithley_instrument.smua.measure.v()
                                # measured_i_gate = keithley_instrument.smub.measure.i()

                                    # record to file
                    info = {
                        'time': time.time() - start_time,
                        'i_channel': measured_i_channel,
                        'v_drain': measured_v_drain,
                                    # 'i_gate': measured_i_gate,
                                                    }
                    logging.info(f"save {info=} to .csv")
                    file_writer.writerow(info)
                except Exception as e:
                                # # ======
                                # # Open all switches
                                # # ======
                                # For the relay board: HIGH = OFF = OPEN // LOW = ON = CLOSE
                    logging.info(f"ERROR: keithley measurement: {e=}")
                    

                                    
                                # Rest between measurement
except KeyboardInterrupt:
     # # ======
        # # Open all switches
        # # ======
    logging.info("Keithley measurement    : EXIT")
            # turn off the keithley
    keithley_instrument.smua.source.output = keithley_instrument.smua.OUTPUT_OFF   # turn off SMUA
    keithley_instrument.smub.source.output = keithley_instrument.smub.OUTPUT_OFF   # turn off SMUB



