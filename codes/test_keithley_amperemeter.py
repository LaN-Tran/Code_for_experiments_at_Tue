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
import csv
import pandas as pd
import matplotlib.animation as animation


    # # ======
    # # Logger
    # # ======
# init logger
format = "%(asctime)s: %(message)s"
log_file_path = 'example.log'
logging.basicConfig(format=format, level=logging.INFO,  
                        datefmt="%H:%M:%S", filename= log_file_path, filemode= 'w')

    # # ======
    # # Keithley
    # # ======
        # init the instrument handle
    # k = Keithley2600('USB0::0x05E6::0x2636::4480001::INSTR', visa_library = 'C:/windows/System32/visa64.dll')
keithley_instrument = Keithley2600('USB0::0x05E6::0x2602::4522205::INSTR', visa_library = 'C:/windows/System32/visa64.dll')
        # Turn everything OFF
keithley_instrument.smua.source.output = keithley_instrument.smua.OUTPUT_OFF   # turn off SMUA
time.sleep(1)

try:

        # # ======
        # # Measurement parameter
        # # ======
    logging.info("Main    : Prepare measurement")

    sw_settle_time = 0.1 # [s]
    keithley_settle_time = 0.5 # [s]
    read_duration = 1 # [s]
    wait_between_read_and_write = 2 # [s]
    nexp = 100
    wait_between_exp = 4

        # # ======
        # # AD3 parameters for read phase
        # # ======
    drain_voltage = 0.2 # [V]
    ad3_settle_time = 0.1 # [s]

        # # ======
        # # AD3 parameters for write phase
        # # ======
    # w1_period = write period -> wait time = 0 [s]
    # w2_period = w1_period - delta_tpre_tpost ; w2 must have wait time = delta_tpre_tpost 
    delta_tpre_tpost = 10e-3 # [s]
    n_write_cycle = 5

    w1_ch_drain = 0 # 
    w1_period = 0.1 # [s]
    w1_pulse_width = 1e-3 # [s]
    w1_freq = 1/(w1_period) # [Hz]
    w1_amplitude = 200e-3 # [V]
    w1_offset = 0 # [V]
    w1_percentageSymmetry =  w1_pulse_width * 100/ w1_period # [%]
    secWait_1 = 0 # [s]
            
    w2_ch_gate = 1
    w2_period = w1_period -  delta_tpre_tpost # [s]
    pulse_width_ch_2 = w1_pulse_width # [s]
    w2_freq = 1/ w2_period # [Hz]
    w2_amplitude = 200e-3 # [V]
    w2_offset = 0 # [V]
    w2_percentageSymmetry = (pulse_width_ch_2 / w2_period) * 100 # pulse width = 100 ms
    secWait_2 =  delta_tpre_tpost # [s]
    
                # ======
                # Configure smua as Amperemeter
                # ======
    logging.info("Configure smua as Amperemeter")
                # PAGE 2-14
    keithley_instrument.smua.reset()

                # (step 1) Select the voltage source function.
    keithley_instrument.smua.source.func = keithley_instrument.smua.OUTPUT_DCVOLTS

                # (step 2)
                ## source side
                # Set the bias voltage to 0 A. (source level)
    keithley_instrument.smua.source.levelv = 0
                # Set the source range to lowest (resolution): 100 mV
                    # ref: https://www.datatec.eu/de/en/keithley-2602b
    keithley_instrument.smua.source.rangev = 100e-3
                # Set the voltage limit (safety) to be higer than in the expected measurement
    keithley_instrument.smua.source.limitv = 1

                ## measure side
                # ? When selecting as current source, 
                # the instrument channel is automatically thought of as voltage meter ?

                # Select measure voltage autorange.
    keithley_instrument.smua.measure.autorangei = keithley_instrument.smua.AUTORANGE_ON
    keithley_instrument.smua.measure.autozero = keithley_instrument.smua.AUTOZERO_OFF

                # Enable 2-wire.
    keithley_instrument.smua.sense = keithley_instrument.smua.SENSE_LOCAL
    
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
    keithley_instrument.smub.source.levelv = 0.5

                    # Select measure I autorange.
    keithley_instrument.smub.measure.autozero = keithley_instrument.smua.AUTOZERO_OFF
    keithley_instrument.smub.measure.autorangei = keithley_instrument.smua.AUTORANGE_ON
    
                # # ======
                # # Turn on Keithley
                # # ======
    logging.info("Turn on Keithley")
    keithley_instrument.smua.source.output = keithley_instrument.smua.OUTPUT_ON
    keithley_instrument.smub.source.output = keithley_instrument.smub.OUTPUT_ON  
    time.sleep(keithley_settle_time)

    wait_time = 1 # [s]
    logging.info("start measurement")
    time_ref = time.time()
    
    # nexp
    for idx_exp in range(0, nexp):
        # read
        # set voltage on drain, configure wave gen for reading and start -> wait to be stable, AD3
        start = time.time()
        current = time.time()
        while (current - start) < wait_time:
            logging.info(" measure from smub")
            measured_i_channel = keithley_instrument.smub.measure.i()
            logging.info(f"measure from B = {measured_i_channel} [A]")
            current = time.time()
        
        logging.info(" outside while loop")
        measured_ia_channel = keithley_instrument.smua.measure.i()
        measured_ib_channel = keithley_instrument.smub.measure.i()
        logging.info(f"measure from A = {measured_ia_channel} [A]")
        logging.info(f"measure from B = {measured_ib_channel} [A]")
        
        
        # wait between exp
        time.sleep(wait_between_exp)

except KeyboardInterrupt:
        # # ======
        # # Open all switches
        # # ======
    logging.info("Keithley measurement    : EXIT")
            # turn off the keithley
    keithley_instrument.smua.source.output = keithley_instrument.smua.OUTPUT_OFF   # turn off SMUA
    keithley_instrument.smub.source.output = keithley_instrument.smub.OUTPUT_OFF   # turn off SMUA