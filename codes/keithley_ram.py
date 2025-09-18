"""
    Automation Keithley 2602B measurement
    Transfer curve experiment
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
keithley_instrument = Keithley2600('USB0::0x05E6::0x2636::4480001::INSTR', visa_library = 'C:/windows/System32/visa64.dll')
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
file_path = "C:/Users/20245580/LabCode/Codes_For_Experiments/exp_data/20250821/ecram.csv"

logging.info("Main    : Prepare measurement")

sw_settle_time = 0.1 # [s]
gate_bias_voltage = 0 # [s]
drain_bias_voltage = 0.2 # [s]
keithley_settle_time = 0.1 # [s]
wait_before_exp = 5 # [s]
nexp = 10
n_pulse_type_1 = 5
amp_pulse_type_1 = -1 # (Vgs > 0, decrease gm. bcz source is always 0, and drain - source are symmertrical)
pulse_width_type_1 = 0.5
pulse_period_type_1 = 1
no_pulse_time_type_1 = pulse_period_type_1 - pulse_width_type_1
wait_between_pulse_type_1 = 1
wait_between_pulse_type_1_and_pulse_type_2 = 1
n_pulse_type_2 = 5
amp_pulse_type_2 = 0.8 # (Vgs < 0, increase gm.  bcz source is always 0, and drain - source are symmertrical)
pulse_width_type_2 = 0.5
pulse_period_type_2 = 1
no_pulse_time_type_2 = pulse_period_type_2 - pulse_width_type_2
wait_between_pulse_type_2 = 1
wait_between_exp = 1

try:
                # ======
                # Prepare switch (still OPEN)
                # ======
     # configure Z - Y1 (write)
    arduino_board.digital[arduino_bin_mux_s0].write(1)
    arduino_board.digital[arduino_bin_mux_s1].write(0)
    arduino_board.digital[arduino_bin_mux_s2].write(0)
    time.sleep(sw_settle_time)
    
                # ======
                # Prepare record file
                # ======
    field_names = ['time', 'i_channel', 'v_gate']
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
    keithley_instrument.smub.measure.autozero = keithley_instrument.smub.AUTOZERO_OFF

                    # Select the voltage source function.
    keithley_instrument.smub.source.func = keithley_instrument.smub.OUTPUT_DCVOLTS
                    
                    # Set the bias voltage.
    keithley_instrument.smub.source.levelv = gate_bias_voltage
                    
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
    keithley_instrument.smua.source.levelv = drain_bias_voltage
                    
                # # ======
                # # Turn on Keithley
                # # ======
    logging.info("Turn on Keithley")
    keithley_instrument.smua.source.output = keithley_instrument.smua.OUTPUT_ON  
    keithley_instrument.smub.source.output = keithley_instrument.smub.OUTPUT_ON  
    time.sleep(keithley_settle_time)

    logging.info("start measurement")
    time_ref = time.time()
    
    # before exp
    logging.info("before exp")
    start_time = time.time()
    current_time = time.time()
    while (current_time - start_time) < wait_before_exp:
        try:
            measured_i_channel = keithley_instrument.smua.measure.i()
            measured_v_gate = keithley_instrument.smub.measure.v()
            # record to file
            with open(file_path, 'a') as file: 
                        # NOTICE: THE WHILE LOOP/ FOR LOOP INSIDE -> NO CONSTANT UPDATE TO FILE AT ALL -> NO ANIMATION
                file_writer = csv.DictWriter(file, fieldnames=field_names)
                info = {
                        'time': time.time() - time_ref,
                        'i_channel': measured_i_channel,
                        'v_gate': measured_v_gate,
                                                    }
                file_writer.writerow(info)
        
        except Exception as CatchError:
            logging.info("ERROR: keithley measure function error")
            logging.info(f"{CatchError=}")

        current_time = time.time()

    # nexp 
    logging.info("start exp")
    for idx_exp in range(0, nexp):
            # n pulse_type_1
            for idx_pulse_type_1 in range (0, n_pulse_type_1):
                # pulse width (close switch)

                    # apply pulse (gate)
                keithley_instrument.smub.source.levelv = amp_pulse_type_1
                    # close switch
                arduino_board.digital[arduino_bin_mux_enable].write(0)
                    # start pulse
                start_time = time.time()
                current_time = time.time()
                while (current_time - start_time) < pulse_width_type_1:
                    try:
                        measured_i_channel = keithley_instrument.smua.measure.i()
                        measured_v_gate = keithley_instrument.smub.measure.v()
                        # record to file
                        with open(file_path, 'a') as file: 
                                    # NOTICE: THE WHILE LOOP/ FOR LOOP INSIDE -> NO CONSTANT UPDATE TO FILE AT ALL -> NO ANIMATION
                            file_writer = csv.DictWriter(file, fieldnames=field_names)
                            info = {
                                    'time': time.time() - time_ref,
                                    'i_channel': measured_i_channel,
                                    'v_gate': measured_v_gate,
                                                                }
                            file_writer.writerow(info)
                    
                    except Exception as CatchError:
                        logging.info("ERROR: keithley measure function error")
                        logging.info(f"{CatchError=}")
                    
                    current_time = time.time()

                # no pulse (open switch)
                    # open switch
                arduino_board.digital[arduino_bin_mux_enable].write(1)
                    # apply bias voltage (gate)
                keithley_instrument.smub.source.levelv = gate_bias_voltage
                    # start record
                start_time = time.time()
                current_time = time.time()
                while (current_time - start_time) < no_pulse_time_type_1:
                    try:
                        measured_i_channel = keithley_instrument.smua.measure.i()
                        measured_v_gate = keithley_instrument.smub.measure.v()
                        # record to file
                        with open(file_path, 'a') as file: 
                                    # NOTICE: THE WHILE LOOP/ FOR LOOP INSIDE -> NO CONSTANT UPDATE TO FILE AT ALL -> NO ANIMATION
                            file_writer = csv.DictWriter(file, fieldnames=field_names)
                            info = {
                                    'time': time.time() - time_ref,
                                    'i_channel': measured_i_channel,
                                    'v_gate': measured_v_gate,
                                                                }
                            file_writer.writerow(info)
                    except Exception as CatchError:
                        logging.info("ERROR: keithley measure function error")
                        logging.info(f"{CatchError=}")
                    
                    current_time = time.time()
                
                # wait between pulse_type_1 (open switch) 
                    # start record
                start_time = time.time()
                current_time = time.time()
                while (current_time - start_time) < wait_between_pulse_type_1:
                    try:
                        measured_i_channel = keithley_instrument.smua.measure.i()
                        measured_v_gate = keithley_instrument.smub.measure.v()
                        # record to file
                        with open(file_path, 'a') as file: 
                                    # NOTICE: THE WHILE LOOP/ FOR LOOP INSIDE -> NO CONSTANT UPDATE TO FILE AT ALL -> NO ANIMATION
                            file_writer = csv.DictWriter(file, fieldnames=field_names)
                            info = {
                                    'time': time.time() - time_ref,
                                    'i_channel': measured_i_channel,
                                    'v_gate': measured_v_gate,
                                                                }
                            file_writer.writerow(info)
                    except Exception as CatchError:
                        logging.info("ERROR: keithley measure function error")
                        logging.info(f"{CatchError=}")
                    
                    current_time = time.time()

            # wait between pulse_type_1 and pulse_type_2 (open switch)
                # start record
            start_time = time.time()
            current_time = time.time()
            while (current_time - start_time) < wait_between_pulse_type_1_and_pulse_type_2:
                try:
                    measured_i_channel = keithley_instrument.smua.measure.i()
                    measured_v_gate = keithley_instrument.smub.measure.v()
                        # record to file
                    with open(file_path, 'a') as file: 
                        file_writer = csv.DictWriter(file, fieldnames=field_names)
                        info = {
                                    'time': time.time() - time_ref,
                                    'i_channel': measured_i_channel,
                                    'v_gate': measured_v_gate,
                                                                }
                        file_writer.writerow(info)
                except Exception as CatchError:
                        logging.info("ERROR: keithley measure function error")
                        logging.info(f"{CatchError=}")
                    
                current_time = time.time()

            # n pulse_type_2 
            for idx_pulse_type_2 in range (0, n_pulse_type_2):
                # pulse width (close switch)

                    # apply pulse (gate)
                keithley_instrument.smub.source.levelv = amp_pulse_type_2
                    # close switch
                arduino_board.digital[arduino_bin_mux_enable].write(0)
                    # start pulse
                start_time = time.time()
                current_time = time.time()
                while (current_time - start_time) < pulse_width_type_2:
                    try:
                        measured_i_channel = keithley_instrument.smua.measure.i()
                        measured_v_gate = keithley_instrument.smub.measure.v()
                        # record to file
                        with open(file_path, 'a') as file: 
                                    # NOTICE: THE WHILE LOOP/ FOR LOOP INSIDE -> NO CONSTANT UPDATE TO FILE AT ALL -> NO ANIMATION
                            file_writer = csv.DictWriter(file, fieldnames=field_names)
                            info = {
                                    'time': time.time() - time_ref,
                                    'i_channel': measured_i_channel,
                                    'v_gate': measured_v_gate,
                                                                }
                            file_writer.writerow(info)
                    except Exception as CatchError:
                        logging.info("ERROR: keithley measure function error")
                        logging.info(f"{CatchError=}")
                    
                    current_time = time.time()

                # no pulse (open switch)
                    # open switch
                arduino_board.digital[arduino_bin_mux_enable].write(1)
                    # apply bias voltage (gate)
                keithley_instrument.smub.source.levelv = gate_bias_voltage
                    # start record
                start_time = time.time()
                current_time = time.time()
                while (current_time - start_time) < no_pulse_time_type_2:
                    try:
                        measured_i_channel = keithley_instrument.smua.measure.i()
                        measured_v_gate = keithley_instrument.smub.measure.v()
                        # record to file
                        with open(file_path, 'a') as file: 
                                    # NOTICE: THE WHILE LOOP/ FOR LOOP INSIDE -> NO CONSTANT UPDATE TO FILE AT ALL -> NO ANIMATION
                            file_writer = csv.DictWriter(file, fieldnames=field_names)
                            info = {
                                    'time': time.time() - time_ref,
                                    'i_channel': measured_i_channel,
                                    'v_gate': measured_v_gate,
                                                                }
                            file_writer.writerow(info)
                    except Exception as CatchError:
                        logging.info("ERROR: keithley measure function error")
                        logging.info(f"{CatchError=}")
                    
                    current_time = time.time()
                
                # wait between pulse_type_2 (open switch) 
                    # start record
                start_time = time.time()
                current_time = time.time()
                while (current_time - start_time) < wait_between_pulse_type_2:
                    try:
                        measured_i_channel = keithley_instrument.smua.measure.i()
                        measured_v_gate = keithley_instrument.smub.measure.v()
                        # record to file
                        with open(file_path, 'a') as file: 
                                    # NOTICE: THE WHILE LOOP/ FOR LOOP INSIDE -> NO CONSTANT UPDATE TO FILE AT ALL -> NO ANIMATION
                            file_writer = csv.DictWriter(file, fieldnames=field_names)
                            info = {
                                    'time': time.time() - time_ref,
                                    'i_channel': measured_i_channel,
                                    'v_gate': measured_v_gate,
                                                                }
                            file_writer.writerow(info)
                    except Exception as CatchError:
                        logging.info("ERROR: keithley measure function error")
                        logging.info(f"{CatchError=}")
                    
                    current_time = time.time()

            # wait between exp (open switch)
                # start record
            start_time = time.time()
            current_time = time.time()
            while (current_time - start_time) < wait_between_exp:
                try:
                    measured_i_channel = keithley_instrument.smua.measure.i()
                    measured_v_gate = keithley_instrument.smub.measure.v()
                        # record to file
                    with open(file_path, 'a') as file: 
                        file_writer = csv.DictWriter(file, fieldnames=field_names)
                        info = {
                                    'time': time.time() - time_ref,
                                    'i_channel': measured_i_channel,
                                    'v_gate': measured_v_gate,
                                                                }
                        file_writer.writerow(info)
                except Exception as CatchError:
                        logging.info("ERROR: keithley measure function error")
                        logging.info(f"{CatchError=}")
                    
                current_time = time.time()


    # end exp
    # # ======
    # # Open all switches
    # # ======
    logging.info("Keithley measurement    : EXIT")
            # disconnect
    arduino_board.digital[arduino_bin_mux_enable].write(1)
            # turn off the keithley
    keithley_instrument.smua.source.output = keithley_instrument.smua.OUTPUT_OFF   # turn off SMUA
    keithley_instrument.smub.source.output = keithley_instrument.smub.OUTPUT_OFF   # turn off SMUB

except KeyboardInterrupt:
        # # ======
        # # Open all switches
        # # ======
    logging.info("Keithley measurement    : EXIT")
            # disconnect
    arduino_board.digital[arduino_bin_mux_enable].write(1)
            # turn off the keithley
    keithley_instrument.smua.source.output = keithley_instrument.smua.OUTPUT_OFF   # turn off SMUA
    keithley_instrument.smub.source.output = keithley_instrument.smub.OUTPUT_OFF   # turn off SMUB
