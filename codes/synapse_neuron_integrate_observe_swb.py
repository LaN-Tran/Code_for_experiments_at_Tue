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

import pyfirmata
import sys

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
        # Other parameters
        # ======
swb_settle = 0.5
number_r_measured_samples = 5
        # ======
        # Arduino, swb to switch between neuron and keithley measurement
        # ======
logging.info(f"Arduino- swb: INIT")
arduino_board = pyfirmata.Arduino('COM10')
arduino_sw_1 = 2 # ( to neuron) same output, different inputs
arduino_sw_2 = 3 ## ( to neuron) same output, different inputs
arduino_sw_3 = 4 # (SMUB - channel resistance measurement)
arduino_sw_4 = 5 ## (connect to SMUB Low/GND)

switch_signal = 1 # (open all switches)
arduino_board.digital[arduino_sw_1].write(switch_signal)
arduino_board.digital[arduino_sw_2].write(switch_signal)
arduino_board.digital[arduino_sw_3].write(switch_signal)
arduino_board.digital[arduino_sw_4].write(switch_signal)
logging.info(f"Arduino- swb: INIT successfully")

comment_exp = input("TURN ON SWITCH POWER TO CONTINUE, enter ON, NO SPACE: ")
logging.info(f"Swb is on")

try: 
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
    pulse_period = 0.1  # [s]
    pulse_width = 0.020 # [s]
    delta_tpre_tpost = 0.05 # [s]
    n_write_cycle = 1
    write_func_complete = delta_tpre_tpost + n_write_cycle*pulse_period

    wait_between_read_and_write = 2 
    wait_osc_setup_keithley_run = 15
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
    file_path = "C:/Users/20245580/LabCode/Codes_For_Experiments/exp_data/20251204\\neuron_synapse_r.csv"
    logging.info("Prepare record file")
    field_names = ['time', 'R']
    if os.path.exists(file_path):
            print("File exists.")
    else:
            print("File not exist. create file")
            with open(file_path, 'a') as file:
                    file_writer = csv.DictWriter(file, fieldnames=field_names)
                    file_writer.writeheader()

    file_path_peak = "C:/Users/20245580/LabCode/Codes_For_Experiments/exp_data/20251204\\neuron_synapse_r_avg.csv"
    logging.info("Prepare record file")
    field_names_peak = ['time', 'Ravg']
    if os.path.exists(file_path_peak):
            print("File exists.")
    else:
            print("File not exist. create file")
            with open(file_path_peak, 'a') as file:
                    file_writer = csv.DictWriter(file, fieldnames=field_names_peak)
                    file_writer.writeheader()

    # start keithley pulse

        # connect ppecram to neuron
    logging.info("SWB: connect ppecram to neuron")
    switch_signal = 0 # (connect all switches)
    arduino_board.digital[arduino_sw_1].write(switch_signal)
    arduino_board.digital[arduino_sw_2].write(switch_signal)
    time.sleep(swb_settle)

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

    # while True:
    #     trigger_sts = osc_rig.query(':TRIG:STAT?')
    #     # print(f"{trigger_sts=}")
    #     if 'STOP' in trigger_sts:
    #             logging.info(f"OSC: {trigger_sts=}")
    #             break 
    #     logging.info(f"OSC: {trigger_sts=}")

    #     time.sleep(0.1) # if the trigger is still waiting, then we wait a bit until the next read


        # reconfigure the keithley smub to measure channel resistance
    logging.info("KEITHLEY: setup smub for resistance measurement")
    keithley_instrument.write('smub.reset()')
    # Select the voltage source function.
    keithley_instrument.write('smub.source.func = smub.OUTPUT_DCVOLTS')
    # set range voltage
    keithley_instrument.write('smub.source.rangev = 1e-3')
    # Set the voltage source level to 50m V
    keithley_instrument.write('smub.source.levelv = 0.05')
    # Set the current limit to 1m A. = safety
    keithley_instrument.write('smub.source.limiti = 1')
    # Enable 2-wire ohms.
    keithley_instrument.write('smub.sense = smub.SENSE_LOCAL')
    # Set the current range to auto.
    keithley_instrument.write('smub.measure.autorangei = smub.AUTORANGE_ON')
    # disconnect ppecram to neuron
    logging.info("SWB: disconnect ppecram - neuron")
    switch_signal = 1 # (open all switches)
    arduino_board.digital[arduino_sw_1].write(switch_signal)
    arduino_board.digital[arduino_sw_2].write(switch_signal)
    time.sleep(swb_settle)
    # switch to keithley for 
    logging.info("SWB: connect ppecram - keithley")
    switch_signal = 0 # (connect all switches)
    arduino_board.digital[arduino_sw_3].write(switch_signal)
    arduino_board.digital[arduino_sw_4].write(switch_signal)
    time.sleep(swb_settle)
    # Turn on KEITHLEY output.
    keithley_instrument.write('smub.source.output = smub.OUTPUT_ON')

    # meassure channel resistance
    measured_r = []
    logging.info("KEITHLEY: R measure")
    for i in range(0, number_r_measured_samples): # make 100 measurement and take average
        try:
            measured_r_channel = float(keithley_instrument.query('print(smub.measure.r())'))
            measured_r.append(measured_r_channel)
            time.sleep(0.1)
        except Exception as CatchError:
            logging.info("ERROR: keithley measure function error")
            logging.info(f"{CatchError=}")
            keithley_instrument.close()
            comment_exp = input("TURN OFF SWITCH POWER TO CONTINUE, enter OFF, NO SPACE: ")
            sys.exit(-1)


    # open switch for Keithley, connect to neuron 
    logging.info("SWB: disconnect ppecram - keithley")
    switch_signal = 1 # (open all switches)
    arduino_board.digital[arduino_sw_3].write(switch_signal)
    arduino_board.digital[arduino_sw_4].write(switch_signal)
    time.sleep(swb_settle)

    logging.info("SWB: connect ppecram - neuron")
    switch_signal = 0 # (close all switches)
    arduino_board.digital[arduino_sw_1].write(switch_signal)
    arduino_board.digital[arduino_sw_2].write(switch_signal)
    time.sleep(swb_settle)

    curr_time = datetime.now()
    with open(file_path, 'a') as file: 
                            # NOTICE: THE WHILE LOOP/ FOR LOOP INSIDE -> NO CONSTANT UPDATE TO FILE AT ALL -> NO ANIMATION
                    file_writer = csv.DictWriter(file, fieldnames=field_names)
                    for i in range(0, len(measured_r)):
                            info = {
                                    'time': curr_time,
                                    'R': measured_r[i]
                                            # 'i_gate': measured_i_gate,
                                                            }
                            
                            file_writer.writerow(info)

    with open(file_path_peak, 'a') as file: 
                            # NOTICE: THE WHILE LOOP/ FOR LOOP INSIDE -> NO CONSTANT UPDATE TO FILE AT ALL -> NO ANIMATION
                    file_writer = csv.DictWriter(file, fieldnames=field_names_peak)
                    info = {
                                    'time': curr_time,
                                    'Ravg': sum(measured_r)/ len(measured_r)
                                            # 'i_gate': measured_i_gate,
                                                            }
                            
                    file_writer.writerow(info)
    logging.info(f"KEITHLEY: Save to file SUC")
    keithley_instrument.write(f"smua.source.output = smua.OUTPUT_OFF")    # turn off SMUA
    keithley_instrument.write(f"smub.source.output = smub.OUTPUT_OFF")    # turn off SMUB
    keithley_instrument.close()

    comment_exp = input("TURN OFF SWITCH POWER TO END, enter OFF, NO SPACE: ")

except KeyboardInterrupt:
        # # ======
        # # Open all switches
        # # ======
    logging.info("Keithley measurement    : EXIT")
            # turn off the keithley
    keithley_instrument.write(f"smua.source.output = smua.OUTPUT_OFF")    # turn off SMUA
    keithley_instrument.write(f"smub.source.output = smub.OUTPUT_OFF")    # turn off SMUB
    keithley_instrument.close()

    comment_exp = input("TURN OFF SWITCH POWER TO END, enter OFF, NO SPACE: ")
    sys.exit(-1)