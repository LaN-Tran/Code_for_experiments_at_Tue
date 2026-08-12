"""
    Automation Keithley 2602B measurement
    RAM experiment
    Author:  Tran Le Phuong Lan.
    Created:  2025-06-05

    Requires:                       
       Python 2.7, 3
    Reference:

"""

# Libs
import pyvisa
import time
import threading
import logging
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
# `keithley_instrument`: for pulsing and sourcing
keithley_instrument = rm.open_resource('USB0::0x05E6::0x2636::4480001::INSTR')
keithley_instrument.timeout = 10000
        # start tsp link
print(keithley_instrument.write("tsplink.reset()"))
        # Turn everything OFF
keithley_instrument.write('node[1].smua.source.output = node[1].smua.OUTPUT_OFF')   # turn off SMUA
keithley_instrument.write('node[1].smub.source.output = node[1].smub.OUTPUT_OFF')   # turn off SMUB

keithley_instrument.write('node[2].smua.source.output = node[2].smua.OUTPUT_OFF')   # turn off SMUA
keithley_instrument.write('node[2].smub.source.output = node[2].smub.OUTPUT_OFF')   # turn off SMUB

time.sleep(1)


        # path to the measurement record
file_path = r"C:\Users\20176985\Downloads\Keithleys_python\data\ecram.csv"

logging.info("Main    : Prepare measurement")

sw_settle_time = 0.1 # [s]
# gate_bias_voltage = 0.2 #[s]
gate_bias_voltage_p1 = 0 #[s]
gate_bias_voltage_p2 = 0 #[s]
drain_bias_voltage = 0.2 # [s]
keithley_settle_time = 0.1 # [s]
wait_before_exp = 1 # [s]
nexp = 1
n_pulse_type_1 = 2
# there is an outer loop for this, to change the amplitude after each exp
step_voltage = 0
amp_pulse_type_1 = 0.6 # (Vgs > 0, decrease gm. bcz source is always 0, and drain - source are symmertrical)
pulse_width_type_1 = 2
pulse_period_type_1 = 5
no_pulse_time_type_1 = pulse_period_type_1 - pulse_width_type_1
wait_between_pulse_type_1 = 1
wait_between_pulse_type_1_and_pulse_type_2 = 1
n_pulse_type_2 = 2
amp_pulse_type_2 = -0.6 # (Vgs < 0, increase gm.  bcz source is always 0, and drain - source are symmertrical)
pulse_width_type_2 = 2
pulse_period_type_2 = 5
no_pulse_time_type_2 = pulse_period_type_2 - pulse_width_type_2
wait_between_pulse_type_2 = 1
wait_between_exp = 1

try:
    
                # ======
                # Prepare record file
                # ======
    field_names = ['time', 'i_channel', 'v_drain','i_gate', 'v_gate', 'v_output']
    with open(file_path, 'w') as file:
        file_writer = csv.DictWriter(file, fieldnames=field_names)
        file_writer.writeheader()

    # ======
    # KEITHLEY FOR SOURCE AND MEASUREMENT
    # ======
                # ======
                # Configure smub as voltage source (Gate)
                # ======
                    # reset the channel
    keithley_instrument.write('node[1].smub.reset()')
                
                # Clear buffer 1.
    keithley_instrument.write('node[1].smub.nvbuffer1.clear()')

                    # Select measure I autorange.
    keithley_instrument.write('node[1].smub.measure.autorangei = node[1].smub.AUTORANGE_ON')
    keithley_instrument.write('node[1].smub.measure.autozero = node[1].smub.AUTOZERO_ONCE')

                    # Select the voltage source function.
    keithley_instrument.write('node[1].smub.source.func = node[1].smub.OUTPUT_DCVOLTS')
                    
                    # Set the bias voltage.
    keithley_instrument.write(f"node[1].smub.source.levelv = {gate_bias_voltage_p1}")
                    
                # # ======
                # # Configure smua as source v, measure i (Drain)
                # # ======
                    # Restore 2600B defaults.
    keithley_instrument.write('node[1].smua.reset()')

                    # Select channel A display.
    keithley_instrument.write('node[1].display.screen = node[1].display.SMUA')

                    # Display current.
    keithley_instrument.write('node[1].display.smua.measure.func = node[1].display.MEASURE_DCAMPS')

                    # Select measure I autorange.
    keithley_instrument.write('node[1].smua.measure.autozero = node[1].smua.AUTOZERO_ONCE')
    keithley_instrument.write('node[1].smua.measure.autorangei = node[1].smua.AUTORANGE_ON')

                    # Select ASCII data format.
                # smu.write('format.data = format.ASCII')

                    # Clear buffer 1.
    keithley_instrument.write('node[1].smua.nvbuffer1.clear()')

                    # Select the source voltage function.
    keithley_instrument.write('node[1].smua.source.func = node[1].smua.OUTPUT_DCVOLTS')

                    # Set the bias voltage.
    keithley_instrument.write(f"node[1].smua.source.levelv = {drain_bias_voltage}")

    # ======
    # KEITHLEY FOR VOLTMETER ONLY
    # ======
                # ======
                # Configure smua as voltmeter
                # ======
                # reset the channel
    keithley_instrument.write('node[2].smua.reset()')
    keithley_instrument.write('node[2].smub.reset()')
                # Clear buffer 1.
    keithley_instrument.write('node[2].smua.nvbuffer1.clear()')
                # Select the current source function.
    keithley_instrument.write('node[2].smua.source.func = node[2].smua.OUTPUT_DCAMPS')
                # Set the source level to 0.
    keithley_instrument.write(f"node[2].smua.source.leveli = {0}")
                # Select lowest source range
    keithley_instrument.write('node[2].smua.source.rangei = 100e-9')
                # MUST set the compliance limit > expected voltage measure
    keithley_instrument.write(f"node[2].smua.source.limitv = 20")
                # set the RANGE for measurement range
    keithley_instrument.write(f"node[2].smua.source.autorangev = node[2].smua.AUTORANGE_ON ")
                      
                    

                # # ======
                # # Turn on Keithley
                # # ======
    logging.info("Turn on Keithley")
    # KEITHLEY: source and measurement
    keithley_instrument.write('node[1].smua.source.output = node[1].smua.OUTPUT_ON')  
    keithley_instrument.write('node[1].smub.source.output = node[1].smub.OUTPUT_ON')
    # KEITHLEY: voltmeter
    keithley_instrument.write('node[2].smua.source.output = node[2].smua.OUTPUT_ON')  
    time.sleep(keithley_settle_time)

    logging.info("start measurement")
    time_ref = time.time()
    
    # before exp
    logging.info("before exp")
    start_time = time.time()
    current_time = time.time()
    while (current_time - start_time) < wait_before_exp:
        try:
            measured_i_channel = float(keithley_instrument.query('print(node[1].smua.measure.i())'))
            measured_v_drain = float(keithley_instrument.query('print(node[1].smua.measure.v())'))
            measured_i_gate =  float(keithley_instrument.query('print(node[1].smub.measure.i())'))
            measured_v_gate = float(keithley_instrument.query('print(node[1].smub.measure.v())'))

            measured_v_output = float(keithley_instrument.query('print(node[2].smua.measure.v())'))

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
                        'v_output': measured_v_output,
                                                    }
                file_writer.writerow(info)
        
        except Exception as CatchError:
            logging.info("ERROR: keithley measure function error")
            logging.info(f"{CatchError=}")

        current_time = time.time()

    # nexp 
    logging.info("start exp")
    for idx_exp in range(0, nexp):
            if abs(amp_pulse_type_1 + step_voltage) < 1:     
                    amp_pulse_type_1 =amp_pulse_type_1 +  step_voltage
            print(f"{idx_exp=} , {amp_pulse_type_1= }")
            # n pulse_type_1
            for idx_pulse_type_1 in range (0, n_pulse_type_1):
                # pulse width (close switch)

                    # apply pulse (gate)
                
                keithley_instrument.write(f"node[1].smub.source.levelv = {amp_pulse_type_1}")
                    # start pulse
                start_time = time.time()
                current_time = time.time()
                while (current_time - start_time) < pulse_width_type_1:
                    try:
                        measured_i_channel = float(keithley_instrument.query('print(node[1].smua.measure.i())'))
                        measured_v_drain = float(keithley_instrument.query('print(node[1].smua.measure.v())'))
                        measured_i_gate =  float(keithley_instrument.query('print(node[1].smub.measure.i())'))
                        measured_v_gate = float(keithley_instrument.query('print(node[1].smub.measure.v())'))

                        measured_v_output = float(keithley_instrument.query('print(node[2].smua.measure.v())'))
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
                                    'v_output': measured_v_output,
                                                                }
                            file_writer.writerow(info)
                    
                    except Exception as CatchError:
                        logging.info("ERROR: keithley measure function error")
                        logging.info(f"{CatchError=}")
                    
                    current_time = time.time()

                # no pulse (open switch)
                    # apply bias voltage (gate)
                keithley_instrument.write(f"node[1].smub.source.levelv = {gate_bias_voltage_p1}")
                    # start record
                start_time = time.time()
                current_time = time.time()
                while (current_time - start_time) < no_pulse_time_type_1:
                    try:
                        measured_i_channel = float(keithley_instrument.query('print(node[1].smua.measure.i())'))
                        measured_v_drain = float(keithley_instrument.query('print(node[1].smua.measure.v())'))
                        measured_i_gate =  float(keithley_instrument.query('print(node[1].smub.measure.i())'))
                        measured_v_gate = float(keithley_instrument.query('print(node[1].smub.measure.v())'))

                        measured_v_output = float(keithley_instrument.query('print(node[2].smua.measure.v())'))
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
                                    'v_output': measured_v_output,
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
                        measured_i_channel = float(keithley_instrument.query('print(node[1].smua.measure.i())'))
                        measured_v_drain = float(keithley_instrument.query('print(node[1].smua.measure.v())'))
                        measured_i_gate =  float(keithley_instrument.query('print(node[1].smub.measure.i())'))
                        measured_v_gate = float(keithley_instrument.query('print(node[1].smub.measure.v())'))

                        measured_v_output = float(keithley_instrument.query('print(node[2].smua.measure.v())'))
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
                                    'v_output': measured_v_output,
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
                    measured_i_channel = float(keithley_instrument.query('print(node[1].smua.measure.i())'))
                    measured_v_drain = float(keithley_instrument.query('print(node[1].smua.measure.v())'))
                    measured_i_gate =  float(keithley_instrument.query('print(node[1].smub.measure.i())'))
                    measured_v_gate = float(keithley_instrument.query('print(node[1].smub.measure.v())'))

                    measured_v_output = float(keithley_instrument.query('print(node[2].smua.measure.v())'))
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
                                'v_output': measured_v_output,
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
                keithley_instrument.write(f"node[1].smub.source.levelv = {amp_pulse_type_2}")
                    # start pulse
                start_time = time.time()
                current_time = time.time()
                while (current_time - start_time) < pulse_width_type_2:
                    try:
                        measured_i_channel = float(keithley_instrument.query('print(node[1].smua.measure.i())'))
                        measured_v_drain = float(keithley_instrument.query('print(node[1].smua.measure.v())'))
                        measured_i_gate =  float(keithley_instrument.query('print(node[1].smub.measure.i())'))
                        measured_v_gate = float(keithley_instrument.query('print(node[1].smub.measure.v())'))

                        measured_v_output = float(keithley_instrument.query('print(node[2].smua.measure.v())'))
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
                                    'v_output': measured_v_output,
                                                                }
                            file_writer.writerow(info)
                    except Exception as CatchError:
                        logging.info("ERROR: keithley measure function error")
                        logging.info(f"{CatchError=}")
                    
                    current_time = time.time()

                # no pulse (open switch)
                    # apply bias voltage (gate)
                keithley_instrument.write(f"node[1].smub.source.levelv = {gate_bias_voltage_p2}")
                    # start record
                start_time = time.time()
                current_time = time.time()
                while (current_time - start_time) < no_pulse_time_type_2:
                    try:
                        measured_i_channel = float(keithley_instrument.query('print(node[1].smua.measure.i())'))
                        measured_v_drain = float(keithley_instrument.query('print(node[1].smua.measure.v())'))
                        measured_i_gate =  float(keithley_instrument.query('print(node[1].smub.measure.i())'))
                        measured_v_gate = float(keithley_instrument.query('print(node[1].smub.measure.v())'))

                        measured_v_output = float(keithley_instrument.query('print(node[2].smua.measure.v())'))
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
                                    'v_output': measured_v_output,
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
                        measured_i_channel = float(keithley_instrument.query('print(node[1].smua.measure.i())'))
                        measured_v_drain = float(keithley_instrument.query('print(node[1].smua.measure.v())'))
                        measured_i_gate =  float(keithley_instrument.query('print(node[1].smub.measure.i())'))
                        measured_v_gate = float(keithley_instrument.query('print(node[1].smub.measure.v())'))

                        measured_v_output = float(keithley_instrument.query('print(node[2].smua.measure.v())'))
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
                                    'v_output': measured_v_output,
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
                    measured_i_channel = float(keithley_instrument.query('print(node[1].smua.measure.i())'))
                    measured_v_drain = float(keithley_instrument.query('print(node[1].smua.measure.v())'))
                    measured_i_gate =  float(keithley_instrument.query('print(node[1].smub.measure.i())'))
                    measured_v_gate = float(keithley_instrument.query('print(node[1].smub.measure.v())'))

                    measured_v_output = float(keithley_instrument.query('print(node[2].smua.measure.v())'))
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
                                'v_output': measured_v_output,
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
            # turn off the keithley
    keithley_instrument.write('node[1].smua.source.output = node[1].smua.OUTPUT_OFF')   # turn off SMUA
    keithley_instrument.write('node[1].smub.source.output = node[1].smub.OUTPUT_OFF')   # turn off SMUB

    keithley_instrument.write('node[2].smua.source.output = node[2].smua.OUTPUT_OFF')   # turn off SMUA

except KeyboardInterrupt:
        # # ======
        # # Open all switches
        # # ======
    logging.info("Keithley measurement    : EXIT")
            # turn off the keithley
    keithley_instrument.write('node[1].smua.source.output = node[1].smua.OUTPUT_OFF')   # turn off SMUA
    keithley_instrument.write('node[1].smub.source.output = node[1].smub.OUTPUT_OFF')   # turn off SMUB

    keithley_instrument.write('node[2].smua.source.output = node[2].smua.OUTPUT_OFF')   # turn off SMUA