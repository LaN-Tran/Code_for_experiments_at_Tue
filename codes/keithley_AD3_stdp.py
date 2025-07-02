"""
    Keithley 2602B and Analog Discover 3 measurement
    stdp experiment
    Author:  Tran Le Phuong Lan.
    Created:  2025-06-05

    Requires:                       
       Python 2.7, 3
    Reference:

    [1] [live plotting data](https://www.youtube.com/watch?v=Ercd-Ip5PfQ&t=563s)
    
    [2] [closing event of matplotlib window](https://matplotlib.org/stable/gallery/event_handling/close_event.html)

    [3] [python timer to track time](https://stackoverflow.com/questions/70058132/how-do-i-make-a-timer-in-python)

    [4] [Idea for relay board connection](https://forum.arduino.cc/t/help-on-my-electronic-project-deployment/1112089)
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
keithley_instrument = Keithley2600('USB0::0x05E6::0x2602::4522205::INSTR', visa_library = 'C:/windows/System32/visa64.dll')
        # Turn everything OFF
keithley_instrument.smua.source.output = keithley_instrument.smua.OUTPUT_OFF   # turn off SMUA
keithley_instrument.smub.source.output = keithley_instrument.smub.OUTPUT_OFF   # turn off SMUB
time.sleep(1)

        # init the arduino board
            # Y0 = read phase (only control gate, drain)
            # Y1 = write phase (control all switches: gate, drain, source)
arduino_bin_mux_z = 10 # (HIGH = OFF/ LOW = ON)

arduino_bin_mux_s0 = 2 # (lsb)
arduino_bin_mux_s1 = 3 #
arduino_bin_mux_s2 = 4 # (msb)

arduino_bin_mux_enable = 6 #

arduino_board = pyfirmata.Arduino('COM8')
    # # ======
    # # Open all switches
    # # ======
    # For the relay board: HIGH = OFF = OPEN // LOW = ON = CLOSE
arduino_board.digital[arduino_bin_mux_enable].write(1)
time.sleep(1)

        # path to the measurement record
file_path = "C:/Users/20245580/LabCode/Codes_For_Experiments/exp_data/20250613/transfer_curve_2Metal.csv"

logging.info("Main    : Prepare measurement")

sw_settle_time = 0.1 # [s]
gate_bias_voltage = 0 # [s]
drain_bias_voltage = -0.2 # [s]
keithley_settle_time = 0.1 # [s]
wait_before_exp = 4 # [s]
nexp = 5
n_pulse_type_1 = 4
amp_pulse_type_1 = 0.2
pulse_width_type_1 = 0.5
pulse_period_type_1 = 1 
no_pulse_time_type_1 = pulse_period_type_1 - pulse_width_type_1
wait_between_pulse_type_1 = 2
wait_between_pulse_type_1_and_pulse_type_2 = 5
n_pulse_type_2 = 3
amp_pulse_type_2 = -0.2
pulse_width_type_2 = 0.5
pulse_period_type_2 = 1 
no_pulse_time_type_2 = pulse_period_type_2 - pulse_width_type_2
wait_between_pulse_type_2 = 1
wait_between_exp = 10

try:
    
                # ======
                # Prepare record file
                # ======
    field_names = ['time', 'i_channel']
    with open(file_path, 'w') as file:
        file_writer = csv.DictWriter(file, fieldnames=field_names)
        file_writer.writeheader()

                # ======
                # Configure smua as Amperemeter
                # ======
                    
                # PAGE 2-14
                keithley_instrument.smub.reset()
                smu.write('smub.reset()')

                # (step 1) Select the voltage source function.
                keithley_instrument.smub.source.func = keithley_instrument.smub.OUTPUT_DCVOLTS
                smu.write('smub.source.func = smub.OUTPUT_DCAMPS')

                # (step 2)
                ## source side
                # Set the bias voltage to 0 A. (source level)
                keithley_instrument.smub.source.levelv = 0
                smu.write('smub.source.leveli = 0.0')
                # Set the source range to lowest (resolution): 100 mV
                    # ref: https://www.datatec.eu/de/en/keithley-2602b
                keithley_instrument.smub.source.rangev = 100e-3
                smu.write('smub.source.rangei = 100e-9')
                # Set the voltage limit (safety) to be higer than in the expected measurement
                keithley_instrument.smub.source.limitv = 1
                smu.write('smub.source.limiti = 1e-3')

                ## measure side
                # ? When selecting as current source, 
                # the instrument channel is automatically thought of as voltage meter ?

                # Select measure voltage autorange.
                smu.write('smub.measure.autorangev = smub.AUTORANGE_ON')

                # Enable 2-wire.
                smu.write('smub.sense = smub.SENSE_LOCAL')
                    
                # # ======
                # # Turn on Keithley
                # # ======
    logging.info("Turn on Keithley")
    keithley_instrument.smua.source.output = keithley_instrument.smua.OUTPUT_ON  
    time.sleep(keithley_settle_time)

    logging.info("start measurement")
    time_ref = time.time()
    
    # nexp
    for idx_exp in range(0, nexp):
        # read
            # close the read switch
            # set voltage on drain, AD3
            # while loop for reading period with SMUA
            # open the read switch
        # wait between read and write
        # write
            # close the write switch
            # wait sw settle time
            # start the AD3 wavegen configure (W1, W2)
            # wait until the AD3 finish
            # open the write switch
        # wait between exp


except KeyboardInterrupt:
        # # ======
        # # Open all switches
        # # ======
    logging.info("Keithley measurement    : EXIT")
            # disconnect
    arduino_board.digital[arduino_bin_mux_enable].write(1)
            # turn off the keithley
    keithley_instrument.smua.source.output = keithley_instrument.smua.OUTPUT_OFF   # turn off SMUA
