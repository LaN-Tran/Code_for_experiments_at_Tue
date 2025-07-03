"""
    Automation Keithley 2602B measurement
    STDP experiment
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

# EXP 1 (copy from ../20250602/intro_lab_auto.ipnb - section **Keitley 2600..** - **EXP 2**)
def keithely_actions_exp_1(keithley_instrument, stime):

    # global tst_global

    # PAGE 2-14
    # ======
    # Configure smub as only voltmeter
    # ======

    # Clear buffer 1.
    keithley_instrument.smub.nvbuffer1.clear()

    # reset the channel
    keithley_instrument.smub.reset()

    # (step 1) Select the current source function.
    keithley_instrument.smub.source.func = keithley_instrument.smub.OUTPUT_DCAMPS

    # (step 2)
    ## source side
    # Set the bias current to 0 A. (source level)
    keithley_instrument.smub.source.leveli = 0.0
    # Set the source range to lowest (resolution): 100 nA
    keithley_instrument.smub.source.rangei = 100e-9
    # Set the current limit (safety) to MUST BE higer than in the expected measurement
    keithley_instrument.smub.source.limiti = 1e-3

    ## measure side
    # ? When selecting as current source, 
    # the instrument channel is automatically thought of as voltage meter ?

    # Select measure voltage autorange.
    keithley_instrument.smub.measure.autorangev = keithley_instrument.smub.AUTORANGE_ON

    # Enable 2-wire.
    keithley_instrument.smub.sense = keithley_instrument.smub.SENSE_LOCAL

    # page 3-8
    # ======
    # Configure smua as source v, measure i
    # ======

    # Restore 2600B defaults.
    keithley_instrument.smua.reset()

    # Select channel A display.
    keithley_instrument.display.screen = keithley_instrument.display.SMUA

    # Display current.
    keithley_instrument.display.smua.measure.func = keithley_instrument.display.MEASURE_DCAMPS

    # Select measure I autorange.
    keithley_instrument.smua.measure.autorangei = keithley_instrument.smua.AUTORANGE_ON

    # Select ASCII data format.
    # smu.write('format.data = format.ASCII')

    # Clear buffer 1.
    keithley_instrument.smua.nvbuffer1.clear()

    # Select the source voltage function.
    keithley_instrument.smua.source.func = keithley_instrument.smua.OUTPUT_DCVOLTS

    # Set the bias voltage to 0 V.
    keithley_instrument.smua.source.levelv = 0.0

    # Turn on the voltmeter on.
    keithley_instrument.smub.source.output = keithley_instrument.smub.OUTPUT_ON

    # Turn on the output source on.
    keithley_instrument.smua.source.output = keithley_instrument.smua.OUTPUT_ON

    for v in range(1, 10):

        value = v * 0.01

        logging.info(f"source v from channel A: {value=} [V]")
        keithley_instrument.smua.source.levelv = value

        time.sleep(stime)

        i_a = keithley_instrument.smua.measure.i()
        logging.info(f"measured i at channel A: {i_a=} [V]")
        # print(f"current measured at A: {i_a}")
        
        v_a = keithley_instrument.smua.measure.v()
        logging.info(f"measured v at channel A: {v_a=} [V]")
        # print(f"voltage measured at A: {v_a}")

        v_b = keithley_instrument.smub.measure.v()
        logging.info(f"measured v at channel B: {v_b=} [V]")
        # print(f"voltage measured at B: {v_b}")
        

        time.sleep(1)

        logging.info(f"after 1s delay measure:")

        i_a_2 = keithley_instrument.smua.measure.i()
        logging.info(f"measured i at channel A: {i_a_2=} [V]")
        # print(f"current measured at A: {i_a}")
        
        v_a_2 = keithley_instrument.smua.measure.v()
        logging.info(f"measured v at channel A: {v_a_2=} [V]")
        # print(f"voltage measured at A: {v_a}")

        v_b_2 = keithley_instrument.smub.measure.v()
        logging.info(f"measured v at channel B: {v_b_2=} [V]")
        # print(f"voltage measured at B: {v_b}")

        logging.info(f"{'='*5}")

        # tst_global = tst_global + 1
    
    keithley_instrument.smua.source.output = keithley_instrument.smua.OUTPUT_OFF   # turn off SMUA
    keithley_instrument.smub.source.output = keithley_instrument.smub.OUTPUT_OFF   # turn off SMUB

# EXP 2 (STDP measurement)
# def keithely_actions_exp_2(keithley_instrument, stime, file_path, stop):
def keithely_actions_exp_2(keithley_instrument, arduino_board, file_path, stop):

        # pulsewidth of the pre-synapse or post-synpse >> 24 ms (due to limit of the communication = code)

    settle_time = 2 # s # after the smu configuration
    
    sw_settle_time = 0.1 # s
    wait_till_read = 0.4 # s
    read_duration = sw_settle_time + wait_till_read + 0.3 # s # >> 20 ms (forth and back with the smu) + sw_settle_time
    write_duration = sw_settle_time*5  # s # > sw_settle_time
    between_read_and_write = 3 # s
    retention_duration = 3 # s

        # voltage configure
    gate_voltage = 0
    drain_voltage_write = 0.4
    drain_voltage_read = -0.1

        # arduino bin
    arduino_bin_mux_z = 10 # (sw control, High = Off/ Low = On)
            # Y0 = read phase (only control gate, drain)
            # Y1 = write phase (control all switches: gate, drain, source)
    arduino_bin_mux_s0 = 2 # (lsb)
    arduino_bin_mux_s1 = 3 #
    arduino_bin_mux_s2 = 4 # (msb)

    arduino_bin_mux_enable = 6 #
    
    
            # ======
            # Prepare record file
            # ======
    field_names = ['time', 'i']
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
    keithley_instrument.smub.measure.autozero = keithley_instrument.smub.AUTOZERO_OFF
    keithley_instrument.smub.measure.autorangei = keithley_instrument.smub.AUTORANGE_ON
    keithley_instrument.smub.measure.autorangev = keithley_instrument.smub.AUTORANGE_ON

                # Select the voltage source function.
    keithley_instrument.smub.source.func = keithley_instrument.smub.OUTPUT_DCVOLTS
                
                # Set the bias voltage to 0 V. (Drain/ Source voltage)
    keithley_instrument.smub.source.levelv = gate_voltage
                # the gate resistance ~ 1M
                # , we want to pump in around 1e-8 A

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

                # Set the bias voltage to 0 V. (Drain/ Source voltage)
    keithley_instrument.smua.source.levelv = drain_voltage_read

            # # ======
            # # Arduino configure
            # # ======
            # For the relay board: HIGH = OFF = OPEN // LOW = ON = CLOSE
                # disenable
    arduino_board.digital[arduino_bin_mux_enable].write(1)
                # configure on switch control signal
    arduino_board.digital[arduino_bin_mux_z].write(0)

    # wait for the open transition to tbe stable
    time.sleep(0.5)

            # # ======
            # # Measuring
            # # ======

                # Turn on the gate source.
    keithley_instrument.smub.source.output = keithley_instrument.smub.OUTPUT_ON

                # Turn on the drain source.
    keithley_instrument.smua.source.output = keithley_instrument.smua.OUTPUT_ON

                # Settling time
    time.sleep(settle_time)
    
    logging.info(f"starting the measurement process")
                # start the measurement reference time
    start_time = time.time()
                # start measurement
    # for i in range(0, number_of_measurements):
    while True:
                
        with open(file_path, 'a') as file: 
                # NOTICE: THE WHILE LOOP/ FOR LOOP INSIDE -> NO CONSTANT UPDATE TO FILE AT ALL -> NO ANIMATION
                    file_writer = csv.DictWriter(file, fieldnames=field_names)
                    
                        # Read before write
                    logging.info(f"Read phase")
                            # read with Vdrain = - 0.01 [V]
                    keithley_instrument.smua.source.levelv = drain_voltage_read
                    time.sleep(settle_time)
                            # start the read phase - Y0 (LOW)
                    arduino_board.digital[arduino_bin_mux_s0].write(0)
                    arduino_board.digital[arduino_bin_mux_s1].write(0)
                    arduino_board.digital[arduino_bin_mux_s2].write(0)

                    arduino_board.digital[arduino_bin_mux_enable].write(0)
                    time.sleep(sw_settle_time)

                    start_read_time = time.time()
                    try:
                        time.sleep(wait_till_read)
                        measured_i_channel = keithley_instrument.smua.measure.i()
                        end_read_time = time.time()
                        time.sleep(read_duration - sw_settle_time - (end_read_time - start_read_time))
                        
                                # end the read phase (HIGH)
                        arduino_board.digital[arduino_bin_mux_enable].write(1)
                                # record to file
                        info = {
                                'time': time.time() - start_time,
                                'i': measured_i_channel
                                            }
                        logging.info(f"save {info=} to .csv")
                        file_writer.writerow(info)

                        logging.info(f"wait between read phase and write phase")
                        time.sleep(between_read_and_write)

                            # Write phase
                        logging.info(f"Write phase")
                                # write at Vdrain = -0.5 V
                        keithley_instrument.smua.source.levelv = drain_voltage_write
                        time.sleep(settle_time)
                                # start write phase - Y1 (LOW)
                        arduino_board.digital[arduino_bin_mux_s0].write(1)
                        arduino_board.digital[arduino_bin_mux_s1].write(0)
                        arduino_board.digital[arduino_bin_mux_s2].write(0)

                        arduino_board.digital[arduino_bin_mux_enable].write(0)
                        time.sleep(sw_settle_time)

                        time.sleep(write_duration - sw_settle_time)
                                # end write phase (HIGH)
                        arduino_board.digital[arduino_bin_mux_enable].write(1)
                        time.sleep(sw_settle_time)

                            # Retain duration
                        time.sleep(retention_duration)

                    except:
                        # # ======
                        # # Open all switches
                        # # ======
                        # For the relay board: HIGH = OFF = OPEN // LOW = ON = CLOSE
                        print(f"read from Keithley ERRO")
                        arduino_board.digital[arduino_bin_mux_s0].write(1)

                        keithley_instrument.smua.source.output = keithley_instrument.smua.OUTPUT_OFF   # turn off SMUA
                        keithley_instrument.smub.source.output = keithley_instrument.smub.OUTPUT_OFF   # turn off SMUB
                        break

        if stop():
            # # ======
            # # Open all switches
            # # ======
            # For the relay board: HIGH = OFF = OPEN // LOW = ON = CLOSE
            arduino_board.digital[arduino_bin_mux_enable].write(1)

            keithley_instrument.smua.source.output = keithley_instrument.smua.OUTPUT_OFF   # turn off SMUA
            keithley_instrument.smub.source.output = keithley_instrument.smub.OUTPUT_OFF   # turn off SMUB
            logging.info("Keithley measurement    : EXIT")
            break
    
    logging.info("Keithley measurement    : EXIT")
    arduino_board.digital[arduino_bin_mux_enable].write(1)

    keithley_instrument.smua.source.output = keithley_instrument.smua.OUTPUT_OFF   # turn off SMUA
    keithley_instrument.smub.source.output = keithley_instrument.smub.OUTPUT_OFF   # turn off SMUB

def keithely_actions_exp_3(keithley_instrument, arduino_board, file_path, stop):

        # pulsewidth of the pre-synapse or post-synpse >> 24 ms (due to limit of the communication = code)

    settle_time = 2 # s # after the smu configuration
    
    sw_settle_time = 0.1 # s
    wait_till_read = 0.4 # s
    read_duration = sw_settle_time + wait_till_read + 0.3 # s # >> 20 ms (forth and back with the smu) + sw_settle_time
    write_duration = sw_settle_time*2  # s # > sw_settle_time
    between_read_and_write = 0.1 # s
    retention_duration = 3 # s

        # voltage configure
    drain_voltage_write = 0.2
    source_voltage = 0.2
    drain_voltage_read = -0.2

        # arduino bin
    arduino_bin_mux_z = 10 # (sw control, High = Off/ Low = On)
            # Y0 = read phase (only control gate, drain)
            # Y1 = write phase (control all switches: gate, drain, source)
    arduino_bin_mux_s0 = 2 # (lsb)
    arduino_bin_mux_s1 = 3 #
    arduino_bin_mux_s2 = 4 # (msb)

    arduino_bin_mux_enable = 6 #
    
    
            # ======
            # Prepare record file
            # ======
    field_names = ['time', 'i']
    with open(file_path, 'w') as file:
        file_writer = csv.DictWriter(file, fieldnames=field_names)
        file_writer.writeheader()

            # ======
            # Configure smub as voltage source (Source)
            # ======
                # reset the channel
    keithley_instrument.smub.reset()
            
                # Clear buffer 1.
    keithley_instrument.smub.nvbuffer1.clear()

                # Select measure I autorange.
    keithley_instrument.smub.measure.autozero = keithley_instrument.smub.AUTOZERO_OFF
    keithley_instrument.smub.measure.autorangei = keithley_instrument.smub.AUTORANGE_ON
    keithley_instrument.smub.measure.autorangev = keithley_instrument.smub.AUTORANGE_ON

                # Select the voltage source function.
    keithley_instrument.smub.source.func = keithley_instrument.smub.OUTPUT_DCVOLTS
                
                # Set the bias voltage to 0 V.
    keithley_instrument.smub.source.levelv = source_voltage

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

                # Set the bias voltage to 0 V. (Drain/ Source voltage)
    keithley_instrument.smua.source.levelv = drain_voltage_read

            # # ======
            # # Arduino configure
            # # ======
            # For the relay board: HIGH = OFF = OPEN // LOW = ON = CLOSE
                # disenable
    arduino_board.digital[arduino_bin_mux_enable].write(1)
                # configure on switch control signal
    arduino_board.digital[arduino_bin_mux_z].write(0)

    # wait for the open transition to tbe stable
    time.sleep(0.5)

            # # ======
            # # Measuring
            # # ======

                # Turn on the gate source.
    keithley_instrument.smub.source.output = keithley_instrument.smub.OUTPUT_ON

                # Turn on the drain source.
    keithley_instrument.smua.source.output = keithley_instrument.smua.OUTPUT_ON

                # Settling time
    time.sleep(settle_time)
    
    logging.info(f"starting the measurement process")
                # start the measurement reference time
    start_time = time.time()
                # start measurement
    # for i in range(0, number_of_measurements):
    while True:
                
        with open(file_path, 'a') as file: 
                # NOTICE: THE WHILE LOOP/ FOR LOOP INSIDE -> NO CONSTANT UPDATE TO FILE AT ALL -> NO ANIMATION
                    file_writer = csv.DictWriter(file, fieldnames=field_names)
                    
                        # Read before write
                    logging.info(f"Read phase")
                            # read with Vdrain = - 0.01 [V]
                    keithley_instrument.smua.source.levelv = drain_voltage_read
                    time.sleep(settle_time)
                            # start the read phase - Y0 (LOW)
                    arduino_board.digital[arduino_bin_mux_s0].write(0)
                    arduino_board.digital[arduino_bin_mux_s1].write(0)
                    arduino_board.digital[arduino_bin_mux_s2].write(0)

                    arduino_board.digital[arduino_bin_mux_enable].write(0)
                    time.sleep(sw_settle_time)

                    start_read_time = time.time()
                    try:
                        time.sleep(wait_till_read)
                        measured_i_channel = keithley_instrument.smua.measure.i()
                        end_read_time = time.time()
                        time.sleep(read_duration - sw_settle_time - (end_read_time - start_read_time))
                        
                                # end the read phase (HIGH)
                        arduino_board.digital[arduino_bin_mux_enable].write(1)
                                # record to file
                        info = {
                                'time': time.time() - start_time,
                                'i': measured_i_channel
                                            }
                        logging.info(f"save {info=} to .csv")
                        file_writer.writerow(info)

                        logging.info(f"wait between read phase and write phase")
                        time.sleep(between_read_and_write)

                            # Write phase
                        logging.info(f"Write phase")
                                # write at Vdrain = -0.5 V
                        keithley_instrument.smua.source.levelv = drain_voltage_write
                        time.sleep(settle_time)
                                # start write phase - Y1 (LOW)
                        arduino_board.digital[arduino_bin_mux_s0].write(1)
                        arduino_board.digital[arduino_bin_mux_s1].write(0)
                        arduino_board.digital[arduino_bin_mux_s2].write(0)

                        arduino_board.digital[arduino_bin_mux_enable].write(0)
                        time.sleep(sw_settle_time)

                        time.sleep(write_duration - sw_settle_time)
                                # end write phase (HIGH)
                        arduino_board.digital[arduino_bin_mux_enable].write(1)
                        time.sleep(sw_settle_time)

                            # Retain duration
                        time.sleep(retention_duration)

                    except:
                        # # ======
                        # # Open all switches
                        # # ======
                        # For the relay board: HIGH = OFF = OPEN // LOW = ON = CLOSE
                        print(f"read from Keithley ERRO")
                        arduino_board.digital[arduino_bin_mux_s0].write(1)

                        keithley_instrument.smua.source.output = keithley_instrument.smua.OUTPUT_OFF   # turn off SMUA
                        keithley_instrument.smub.source.output = keithley_instrument.smub.OUTPUT_OFF   # turn off SMUB
                        break

        if stop():
            # # ======
            # # Open all switches
            # # ======
            # For the relay board: HIGH = OFF = OPEN // LOW = ON = CLOSE
            arduino_board.digital[arduino_bin_mux_enable].write(1)

            keithley_instrument.smua.source.output = keithley_instrument.smua.OUTPUT_OFF   # turn off SMUA
            keithley_instrument.smub.source.output = keithley_instrument.smub.OUTPUT_OFF   # turn off SMUB
            logging.info("Keithley measurement    : EXIT")
            break
    
    logging.info("Keithley measurement    : EXIT")
    arduino_board.digital[arduino_bin_mux_enable].write(1)

    keithley_instrument.smua.source.output = keithley_instrument.smua.OUTPUT_OFF   # turn off SMUA
    keithley_instrument.smub.source.output = keithley_instrument.smub.OUTPUT_OFF   # turn off SMUB

# EXP 3 (sweep gate, fix drain, ground source// measure drain + gate current)
def transfer_curve(keithley_instrument, arduino_board, file_path, stop):

    number_of_measurements = 1
    # pulsewidth of the pre-synapse or post-synpse >> 24 ms (due to limit of the communication = code)

    settle_time = 1 # s # after the smu configuration
    
    sw_settle_time = 10e-3 # s
    rest_duration = 1 # s

    gate_voltage_smallest = -0.5 # V (for liquid electrolite)
    gate_voltage_largest = 0.5 # V (for liquid electrolite)
    gate_voltage_step = 0.1 # V
    drain_voltage = -0.1 # V

        # arduino bin
            # Y0 = read phase (only control gate, drain)
            # Y1 = write phase (control all switches: gate, drain, source)
    arduino_bin_mux_z = 10 # (sw control, High = Off/ Low = On)
    arduino_bin_mux_s0 = 2 # (lsb)
    arduino_bin_mux_s1 = 3 #
    arduino_bin_mux_s2 = 4 # (msb)

    arduino_bin_mux_enable = 6 #
    
            # ======
            # Prepare record file
            # ======
    field_names = ['time', 'i_channel', 'v_gate', 'i_gate']
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
    keithley_instrument.smub.source.levelv = gate_voltage_smallest

                # Select measure I autorange.
    keithley_instrument.smub.measure.autozero = keithley_instrument.smua.AUTOZERO_OFF
    keithley_instrument.smub.measure.autorangei = keithley_instrument.smua.AUTORANGE_ON
                

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
            # # Arduino configure to change to write phase connection for sweep
            # # ======
            
            # disconnect
    arduino_board.digital[arduino_bin_mux_enable].write(1)
            # turn on the switch (high = off/ low = on)
    arduino_board.digital[arduino_bin_mux_z].write(0)
            # configure Z - Y1 (write)
    arduino_board.digital[arduino_bin_mux_s0].write(1)
    arduino_board.digital[arduino_bin_mux_s1].write(0)
    arduino_board.digital[arduino_bin_mux_s2].write(0)
    time.sleep(sw_settle_time)
            # connect = close the switches 
    arduino_board.digital[arduino_bin_mux_enable].write(0)

    # wait for the open transition to tbe stable
    time.sleep(0.5)

            # # ======
            # # Measuring
            # # ======

                # Turn on the gate source.
    keithley_instrument.smub.source.output = keithley_instrument.smub.OUTPUT_ON

                # Turn on the drain source.
    keithley_instrument.smua.source.output = keithley_instrument.smua.OUTPUT_ON

                # Settling time
    time.sleep(settle_time)

                # prepare the sweep voltage
    voltage_list_forward = np.arange(gate_voltage_smallest, gate_voltage_largest, gate_voltage_step).tolist()
    voltage_list_backward = np.arange(gate_voltage_largest, gate_voltage_smallest, -gate_voltage_step).tolist()
    logging.info(f"starting the measurement process")
                # start the measurement reference time
    start_time = time.time()
                # start measurement
    for i in range(0, number_of_measurements):
        # forward 
        for idx, v in enumerate(voltage_list_forward):     
            with open(file_path, 'a') as file: 
                    # NOTICE: THE WHILE LOOP/ FOR LOOP INSIDE -> NO CONSTANT UPDATE TO FILE AT ALL -> NO ANIMATION
                        file_writer = csv.DictWriter(file, fieldnames=field_names)
                        
                            # set the voltage (gate)
                        logging.info(f"set gate voltage {v=}")
                        keithley_instrument.smub.source.levelv = v
                        time.sleep(settle_time)
                        try:
                            measured_i_channel = keithley_instrument.smua.measure.i()
                            measured_v_gate = keithley_instrument.smub.measure.v()
                            # measured_i_gate = keithley_instrument.smub.measure.i()

                                # record to file
                            info = {
                                    'time': time.time() - start_time,
                                    'i_channel': measured_i_channel,
                                    'v_gate': measured_v_gate,
                                    # 'i_gate': measured_i_gate,
                                                }
                            logging.info(f"save {info=} to .csv")
                            file_writer.writerow(info)

                        except:
                            # # ======
                            # # Open all switches
                            # # ======
                            # For the relay board: HIGH = OFF = OPEN // LOW = ON = CLOSE
                            print(f"read from Keithley ERRO")
                            arduino_board.digital[arduino_bin_mux_enable].write(1)

                            # turn off keithley
                            keithley_instrument.smua.source.output = keithley_instrument.smua.OUTPUT_OFF   # turn off SMUA
                            keithley_instrument.smub.source.output = keithley_instrument.smub.OUTPUT_OFF   # turn off SMUB
                            break

                                
                            # Rest between measurement
                        time.sleep(rest_duration)
        
            # connect = close the switches 
        arduino_board.digital[arduino_bin_mux_enable].write(0)

        # wait for the open transition to tbe stable
        time.sleep(0.5)

                # # ======
                # # Measuring
                # # ======

                    # Turn on the gate source.
        keithley_instrument.smub.source.output = keithley_instrument.smub.OUTPUT_ON

                    # Turn on the drain source.
        keithley_instrument.smua.source.output = keithley_instrument.smua.OUTPUT_ON

                    # Settling time
        time.sleep(settle_time)

        # backward
        for idx, v in enumerate(voltage_list_backward):     
            with open(file_path, 'a') as file: 
                    # NOTICE: THE WHILE LOOP/ FOR LOOP INSIDE -> NO CONSTANT UPDATE TO FILE AT ALL -> NO ANIMATION
                        file_writer = csv.DictWriter(file, fieldnames=field_names)
                        
                            # set the voltage (gate)
                        logging.info(f"set gate voltage {v=}")
                        keithley_instrument.smub.source.levelv = v
                        time.sleep(settle_time)
                        try:
                            measured_i_channel = keithley_instrument.smua.measure.i()
                            measured_v_gate = keithley_instrument.smub.measure.v()
                            # measured_i_gate = keithley_instrument.smub.measure.i()
                                # record to file
                            info = {
                                    'time': time.time() - start_time,
                                    'i_channel': measured_i_channel,
                                    'v_gate': measured_v_gate,
                                    # 'i_gate': measured_i_gate,
                                                }
                            logging.info(f"save {info=} to .csv")
                            file_writer.writerow(info)

                        except:
                            # # ======
                            # # Open all switches
                            # # ======
                            # For the relay board: HIGH = OFF = OPEN // LOW = ON = CLOSE
                            print(f"read from Keithley ERRO")
                            arduino_board.digital[arduino_bin_mux_enable].write(1)

                            # turn off keithley
                            keithley_instrument.smua.source.output = keithley_instrument.smua.OUTPUT_OFF   # turn off SMUA
                            keithley_instrument.smub.source.output = keithley_instrument.smub.OUTPUT_OFF   # turn off SMUB
                            break

                                
                            # Rest between measurement
                        time.sleep(rest_duration)
        if stop():
            # # ======
            # # Open all switches
            # # ======
                # disconnect
            arduino_board.digital[arduino_bin_mux_enable].write(1)
                # turn off the keithley
            keithley_instrument.smua.source.output = keithley_instrument.smua.OUTPUT_OFF   # turn off SMUA
            keithley_instrument.smub.source.output = keithley_instrument.smub.OUTPUT_OFF   # turn off SMUB
            
            logging.info("Keithley measurement    : EXIT")
            break
    
    # # ======
    # # Open all switches
    # # ======
    logging.info("Keithley measurement    : EXIT")
        # disconnect
    arduino_board.digital[arduino_bin_mux_enable].write(1)
        # turn off the keithley
    keithley_instrument.smua.source.output = keithley_instrument.smua.OUTPUT_OFF   # turn off SMUA
    keithley_instrument.smub.source.output = keithley_instrument.smub.OUTPUT_OFF   # turn off SMUB
                
# EXP 3 (sweep gate, fix drain, ground source// measure drain + gate current)
# EXP 3 (sweep gate, fix drain, ground source// measure drain + gate current)
def transfer_curve_2Metal(keithley_instrument, arduino_board, file_path, stop):

    number_of_measurements = 5
    # pulsewidth of the pre-synapse or post-synpse >> 24 ms (due to limit of the communication = code)

    settle_time = 1 # s # after the smu configuration
    
    sw_settle_time = 10e-3 # s
    rest_duration = 0.1 # s

    gate_voltage_smallest = -1 # V (for liquid electrolite)
    gate_voltage_largest = 1 # V (for liquid electrolite)
    gate_voltage_step = 0.01 # V
    drain_voltage = 0 # V

        # arduino bin
            # Y0 = read phase (only control gate, drain)
            # Y1 = write phase (control all switches: gate, drain, source)
    arduino_bin_mux_z = 10 # (sw control, High = Off/ Low = On)
    arduino_bin_mux_s0 = 2 # (lsb)
    arduino_bin_mux_s1 = 3 #
    arduino_bin_mux_s2 = 4 # (msb)

    arduino_bin_mux_enable = 6 #
    
            # ======
            # Prepare record file
            # ======
    field_names = ['time', 'i_channel', 'v_gate', 'i_gate']
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
    keithley_instrument.smub.source.levelv = gate_voltage_smallest

                # Select measure I autorange.
    keithley_instrument.smub.measure.autozero = keithley_instrument.smua.AUTOZERO_OFF
    keithley_instrument.smub.measure.autorangei = keithley_instrument.smua.AUTORANGE_ON
                

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
            # # Arduino configure to change to write phase connection for sweep
            # # ======
            
            # disconnect
    arduino_board.digital[arduino_bin_mux_enable].write(1)
            # turn on the switch (high = off/ low = on)
    arduino_board.digital[arduino_bin_mux_z].write(0)
            # configure Z - Y1 (write)
    arduino_board.digital[arduino_bin_mux_s0].write(1)
    arduino_board.digital[arduino_bin_mux_s1].write(0)
    arduino_board.digital[arduino_bin_mux_s2].write(0)
    time.sleep(sw_settle_time)
            # connect = close the switches 
    arduino_board.digital[arduino_bin_mux_enable].write(0)

    # wait for the open transition to tbe stable
    time.sleep(0.5)

            # # ======
            # # Measuring
            # # ======

                # Turn on the gate source.
    keithley_instrument.smub.source.output = keithley_instrument.smub.OUTPUT_ON

                # Turn on the drain source.
    keithley_instrument.smua.source.output = keithley_instrument.smua.OUTPUT_ON

                # Settling time
    time.sleep(settle_time)

                # prepare the sweep voltage
    voltage_list_forward_1 = np.arange(0, gate_voltage_largest, gate_voltage_step).tolist()
    voltage_list_forward_2 = np.arange(gate_voltage_largest, 0, -gate_voltage_step)
    voltage_list_forward = np.concatenate((voltage_list_forward_1, voltage_list_forward_2), axis=0)

    voltage_list_backward_1 = np.arange(0, gate_voltage_smallest, -gate_voltage_step).tolist()
    voltage_list_backward_2 = np.arange(gate_voltage_smallest, 0, gate_voltage_step).tolist()
    voltage_list_backward = np.concatenate((voltage_list_backward_1, voltage_list_backward_2), axis=0)
    logging.info(f"starting the measurement process")
                # start the measurement reference time
    start_time = time.time()
                # start measurement
    for i in range(0, number_of_measurements):
        # forward 
        for idx, v in enumerate(voltage_list_forward):     
            with open(file_path, 'a') as file: 
                    # NOTICE: THE WHILE LOOP/ FOR LOOP INSIDE -> NO CONSTANT UPDATE TO FILE AT ALL -> NO ANIMATION
                        file_writer = csv.DictWriter(file, fieldnames=field_names)
                        
                            # set the voltage (gate)
                        logging.info(f"set gate voltage {v=}")
                        keithley_instrument.smub.source.levelv = v
                        time.sleep(settle_time)
                        try:
                            measured_v_gate = keithley_instrument.smub.measure.v()
                            measured_i_gate = keithley_instrument.smub.measure.i()

                                # record to file
                            info = {
                                    'time': time.time() - start_time,
                                    'v_gate': measured_v_gate,
                                    'i_gate': measured_i_gate
                                                }
                            logging.info(f"save {info=} to .csv")
                            file_writer.writerow(info)

                        except:
                            # # ======
                            # # Open all switches
                            # # ======
                            # For the relay board: HIGH = OFF = OPEN // LOW = ON = CLOSE
                            print(f"read from Keithley ERRO")
                            arduino_board.digital[arduino_bin_mux_enable].write(1)

                            # turn off keithley
                            keithley_instrument.smua.source.output = keithley_instrument.smua.OUTPUT_OFF   # turn off SMUA
                            keithley_instrument.smub.source.output = keithley_instrument.smub.OUTPUT_OFF   # turn off SMUB
                            break

                                
                            # Rest between measurement
                        time.sleep(rest_duration)

                        if stop():
                            # # ======
                            # # Open all switches
                            # # ======
                                # disconnect
                            arduino_board.digital[arduino_bin_mux_enable].write(1)
                                # turn off the keithley
                            keithley_instrument.smua.source.output = keithley_instrument.smua.OUTPUT_OFF   # turn off SMUA
                            keithley_instrument.smub.source.output = keithley_instrument.smub.OUTPUT_OFF   # turn off SMUB
                            
                            logging.info("Keithley measurement    : EXIT")
                            break
        
            # connect = close the switches 
        arduino_board.digital[arduino_bin_mux_enable].write(0)

        # wait for the open transition to tbe stable
        time.sleep(0.5)

                # # ======
                # # Measuring
                # # ======

                    # Turn on the gate source.
        keithley_instrument.smub.source.output = keithley_instrument.smub.OUTPUT_ON

                    # Turn on the drain source.
        keithley_instrument.smua.source.output = keithley_instrument.smua.OUTPUT_ON

                    # Settling time
        time.sleep(settle_time)

        # backward
        for idx, v in enumerate(voltage_list_backward):     
            with open(file_path, 'a') as file: 
                    # NOTICE: THE WHILE LOOP/ FOR LOOP INSIDE -> NO CONSTANT UPDATE TO FILE AT ALL -> NO ANIMATION
                        file_writer = csv.DictWriter(file, fieldnames=field_names)
                        
                            # set the voltage (gate)
                        logging.info(f"set gate voltage {v=}")
                        keithley_instrument.smub.source.levelv = v
                        time.sleep(settle_time)
                        try:
                            measured_v_gate = keithley_instrument.smub.measure.v()
                            measured_i_gate = keithley_instrument.smub.measure.i()
                                # record to file
                            info = {
                                    'time': time.time() - start_time,
                                    'v_gate': measured_v_gate,
                                    'i_gate': measured_i_gate
                                                }
                            logging.info(f"save {info=} to .csv")
                            file_writer.writerow(info)

                        except:
                            # # ======
                            # # Open all switches
                            # # ======
                            # For the relay board: HIGH = OFF = OPEN // LOW = ON = CLOSE
                            print(f"read from Keithley ERRO")
                            arduino_board.digital[arduino_bin_mux_enable].write(1)

                            # turn off keithley
                            keithley_instrument.smua.source.output = keithley_instrument.smua.OUTPUT_OFF   # turn off SMUA
                            keithley_instrument.smub.source.output = keithley_instrument.smub.OUTPUT_OFF   # turn off SMUB
                            break

                                
                            # Rest between measurement
                        time.sleep(rest_duration)

                        if stop():
                            # # ======
                            # # Open all switches
                            # # ======
                                # disconnect
                            arduino_board.digital[arduino_bin_mux_enable].write(1)
                                # turn off the keithley
                            keithley_instrument.smua.source.output = keithley_instrument.smua.OUTPUT_OFF   # turn off SMUA
                            keithley_instrument.smub.source.output = keithley_instrument.smub.OUTPUT_OFF   # turn off SMUB
                            
                            logging.info("Keithley measurement    : EXIT")
                            break
        if stop():
            # # ======
            # # Open all switches
            # # ======
                # disconnect
            arduino_board.digital[arduino_bin_mux_enable].write(1)
                # turn off the keithley
            keithley_instrument.smua.source.output = keithley_instrument.smua.OUTPUT_OFF   # turn off SMUA
            keithley_instrument.smub.source.output = keithley_instrument.smub.OUTPUT_OFF   # turn off SMUB
            
            logging.info("Keithley measurement    : EXIT")
            break
    
    # # ======
    # # Open all switches
    # # ======
    logging.info("Keithley measurement    : EXIT")
        # disconnect
    arduino_board.digital[arduino_bin_mux_enable].write(1)
        # turn off the keithley
    keithley_instrument.smua.source.output = keithley_instrument.smua.OUTPUT_OFF   # turn off SMUA
    keithley_instrument.smub.source.output = keithley_instrument.smub.OUTPUT_OFF   # turn off SMUB

def read_from_file_and_plot (_, file_path):
    # global file_path
    data = pd.read_csv(file_path)
    x = data['time']
    y = data['i']

    plt.cla()
    plt.plot(x, y)


def try_arduino_board(board):
    while True:
        print(f"HIGH")
        # For the relay board: HIGH = OFF
        board.digital[9].write(1) # digital pin 13 = built-in LED
        board.digital[10].write(1) # digital pin 13 = built-in LED
        time.sleep(1) # second
        # print(f"LOW")
        # # For the relay board: LOW = ON
        # board.digital[9].write(0)
        # board.digital[10].write(0)
        # time.sleep(1)

        
if __name__ == "__main__":

        # init logger
    format = "%(asctime)s: %(message)s"
    log_file_path = 'example.log'
    logging.basicConfig(format=format, level=logging.INFO,  
                        datefmt="%H:%M:%S", filename= log_file_path, filemode= 'w')

        # init the instrument handle
    # k = Keithley2600('USB0::0x05E6::0x2636::4480001::INSTR', visa_library = 'C:/windows/System32/visa64.dll')
    k = Keithley2600('USB0::0x05E6::0x2602::4522205::INSTR', visa_library = 'C:/windows/System32/visa64.dll')
        # Turn everything OFF
    k.smua.source.output = k.smua.OUTPUT_OFF   # turn off SMUA
    k.smub.source.output = k.smub.OUTPUT_OFF   # turn off SMUB
    time.sleep(1)
        # init the arduino board
            # Y0 = read phase (only control gate, drain)
            # Y1 = write phase (control all switches: gate, drain, source)
    arduino_bin_mux_z = 10 # (HIGH = OFF/ LOW = ON)

    arduino_bin_mux_s0 = 2 # (lsb)
    arduino_bin_mux_s1 = 3 #
    arduino_bin_mux_s2 = 4 # (msb)

    arduino_bin_mux_enable = 6 #

    board = pyfirmata.Arduino('COM8')
    # # ======
    # # Open all switches
    # # ======
    # For the relay board: HIGH = OFF = OPEN // LOW = ON = CLOSE
    board.digital[arduino_bin_mux_enable].write(1)
    time.sleep(1)
        # path to the measurement record
    # file_path = "C:/Users/20245580/LabCode/Automate_Lab_Instrument/20250605/output_exp3.csv"
    # file_path = "C:/Users/20245580/LabCode/Automate_Lab_Instrument/20250605/output_exp_ecram.csv"
    file_path = "C:/Users/20245580/LabCode/Codes_For_Experiments/exp_data/20250613/transfer_curve_2Metal.csv"

    logging.info("Main    : Prepare measurement")

    stop_keithley_write_threads = False
    # xw = threading.Thread(target=transfer_curve, daemon=True, args=(k, board, file_path, lambda: stop_keithley_write_threads, ))
    # xw = threading.Thread(target=keithely_actions_exp_2, daemon=True, args=(k, board, file_path, lambda: stop_keithley_write_threads, )) 
    # xw = threading.Thread(target=keithely_actions_exp_3, daemon=True, args=(k, board, file_path, lambda: stop_keithley_write_threads, ))
    xw = threading.Thread(target=transfer_curve_2Metal, daemon=True, args=(k, board, file_path, lambda: stop_keithley_write_threads, ))
    
    logging.info("Main    : Run measurement")
    xw.start()

    while True:
        
         print(f"input 'stop_thread', then 'stop_main':  ")
         input_str = str(input())

         match input_str:
                case "stop_thread":
                   stop_keithley_write_threads = True
                case "stop_main":
                    if stop_keithley_write_threads == True:
                        break
                    else:
                         pass
    
    logging.info("Main    : EXIT")



        # Trial
            ## 4
    # board.digital[9].write(1)
    # board.digital[10].write(1)
    # print(f"Test board")

    # for i in range(0, 3):
    #     print(f"Test board: {i}")
        
    #     board.digital[9].write(0)
    #     time.sleep(1)
    #     board.digital[9].write(1)
    #     time.sleep(1)
        
    #     board.digital[10].write(0)
    #     time.sleep(1)
    #     board.digital[10].write(1)
    #     time.sleep(1)

    # print(f"End Test board")
    # board.digital[9].write(1)
    # board.digital[10].write(1)
            ## 3
        # init the arduino board
    # board.digital[arduino_bin_mux_z].write(0)
    # board.digital[arduino_bin_mux_enable].write(1)
    # print(f"Test board")

    # for i in range(0, 3):
    #     print(f"Test board: {i}")
    #             # turn on the switch (high = off/ low = on)
        
    #             # configure Z - Y1 (write)
    #     board.digital[arduino_bin_mux_s0].write(1)
    #     board.digital[arduino_bin_mux_s1].write(0)
    #     board.digital[arduino_bin_mux_s2].write(0)
    #     time.sleep(0.1)
    #             # connect = close the switches 
    #     print(f"write (4) connect")
    #     board.digital[arduino_bin_mux_enable].write(0)

    #     # wait for the open transition to tbe stable
    #     time.sleep(2)

    #     print(f"write disconnect")
    #     board.digital[arduino_bin_mux_enable].write(1)
    #     time.sleep(1)

    #             # read phase
    #     # configure Z - Y1 (read)
    #     board.digital[arduino_bin_mux_s0].write(0)
    #     board.digital[arduino_bin_mux_s1].write(0)
    #     board.digital[arduino_bin_mux_s2].write(0)
    #     time.sleep(0.1)
    #     print(f"=read (5) connect")
    #     board.digital[arduino_bin_mux_enable].write(0)
    #     time.sleep(2)
    #     # disconnect
    #     print(f"= read disconnect")
    #     board.digital[arduino_bin_mux_enable].write(1)
    #     time.sleep(2)

    # print(f"End Test board")

    # print(f"disconnect")
    # board.digital[arduino_bin_mux_enable].write(1)
    #         ## 2
    # while True:
    #     board.digital[10].write(1) # digital pin 13 = built-in LED
    #     time.sleep(5) # second
    #     board.digital[10].write(0)
    #     time.sleep(5)






