"""
    Keithley 2602B and Analog Discover 3 measurement
    ecram pulse drain experiment
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

from ctypes import *
import sys
from os import sep  

if sys.platform.startswith("win"):
    dwf = cdll.dwf
    constants_path = "C:" + sep + "Program Files (x86)" + sep + "Digilent" + sep + "WaveFormsSDK" + sep + "samples" + sep + "py"
elif sys.platform.startswith("darwin"): # on macOS
    dwf = cdll.LoadLibrary("/Library/Frameworks/dwf.framework/dwf")
else: # on Linux
    dwf = cdll.LoadLibrary("libdwf.so")
    constants_path = sep + "usr" + sep + "share" + sep + "digilent" + sep + "waveforms" + sep + "samples" + sep + "py"

# Import constans
sys.path.append(constants_path)
import dwfconstants


if sys.platform.startswith("win"):
    dwf = cdll.dwf
elif sys.platform.startswith("darwin"):
    dwf = cdll.LoadLibrary("/Library/Frameworks/dwf.framework/dwf")
else:
    dwf = cdll.LoadLibrary("libdwf.so")

    # # ======
    # # Logger
    # # ======
# init logger
format = "%(asctime)s: %(message)s"
log_file_path = 'example.log'
logging.basicConfig(format=format, level=logging.INFO,  
                        datefmt="%H:%M:%S", filename= log_file_path, filemode= 'w')
    # # ======
    # # AD3 connect
    # # ======
logging.info("AD3 connect")
#declare ctype variables
hdwf = c_int()
sts = c_byte()
#print(DWF version
version = create_string_buffer(16)
dwf.FDwfGetVersion(version)
logging.info("DWF Version: "+str(version.value))

#open device
logging.info("Opening first device")
dwf.FDwfDeviceOpen(c_int(-1), byref(hdwf))

if hdwf.value == dwfconstants.hdwfNone.value:
    szerr = create_string_buffer(512)
    dwf.FDwfGetLastErrorMsg(szerr)
    print(str(szerr.value))
    print("failed to open device")
    quit()

dwf.FDwfDeviceAutoConfigureSet(hdwf, c_int(0)) # 0 = the device will only be configured when FDwf###Configure is called

    # # ======
    # # Keithley
    # # ======
        # init the instrument handle
    # k = Keithley2600('USB0::0x05E6::0x2636::4480001::INSTR', visa_library = 'C:/windows/System32/visa64.dll')
keithley_instrument = Keithley2600('USB0::0x05E6::0x2636::4480001::INSTR', visa_library = 'C:/windows/System32/visa64.dll')
        # Turn everything OFF
keithley_instrument.smua.source.output = keithley_instrument.smua.OUTPUT_OFF   # turn off SMUA
time.sleep(1)

    # # ======
    # # Switch board
    # # ======
        # Y0: read
        # Y1: write
        # init the arduino board
            # Y0 = read phase (only control gate, drain)
            # Y1 = write phase (control all switches: gate, drain, source)
arduino_bin_mux_z = 10 # (HIGH = OFF/ LOW = ON)

arduino_bin_mux_s0 = 2 # (lsb)
arduino_bin_mux_s1 = 3 #
arduino_bin_mux_s2 = 4 # (msb)

arduino_bin_mux_enable = 6 #

arduino_board = pyfirmata.Arduino('COM8')
    # # Open all switches
    # For the relay board: HIGH = OFF = OPEN // LOW = ON = CLOSE
arduino_board.digital[arduino_bin_mux_enable].write(1)
time.sleep(1)

    # # ======
    # # Record file
    # # ======
        # path to the measurement record
file_path = "C:/Users/20245580/LabCode/Codes_For_Experiments/exp_data/20250711/ecram_keithley_AD3_oect6.csv"


try:

        # # ======
        # # Measurement parameter
        # # ======
    logging.info("Main    : Prepare measurement")

    sw_settle_time = 0.5 # [s]
    keithley_settle_time = 0.5 # [s]
    read_duration = 0.5 # [s]
    wait_between_read_and_write = 4 # [s]
    nexp = 100
    wait_between_exp = 4

        # # ======
        # # AD3 parameters for read phase
        # # ======
    drain_voltage = 0.2 # [V]
    ad3_settle_time = 0.5 # [s]

        # # ======
        # # AD3 parameters for write phase
        # # ======
    # w1_period = write period -> wait time = 0 [s]
    # w2_period = w1_period - delta_tpre_tpost ; w2 must have wait time = delta_tpre_tpost 
    n_write_cycle = 1

    w1_ch_drain = 0 # 
    w1_period = 2 # [s]
    pulse_width_ch_1 = 1 # [s]
    w1_freq = 1/ w1_period # [Hz]
    w1_amplitude = 200e-3 # [V]
    w1_offset = 0 # [V]
    w1_percentageSymmetry = (pulse_width_ch_1 / w1_period) * 100 # pulse width = 100 ms
    
            
    w2_ch_gate = 1
    gate_voltage = 0 # [V]
                # ======
                # Prepare record file
                # ======
    logging.info("Prepare record file")
    field_names = ['time', 'i_channel']
    with open(file_path, 'w') as file:
        file_writer = csv.DictWriter(file, fieldnames=field_names)
        file_writer.writeheader()

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

                # Select channel A display.
    keithley_instrument.display.screen = keithley_instrument.display.SMUA

                # Display current.
    keithley_instrument.display.smua.measure.func = keithley_instrument.display.MEASURE_DCAMPS

    
                    
                # # ======
                # # Turn on Keithley
                # # ======
    logging.info("Turn on Keithley")
    keithley_instrument.smua.source.output = keithley_instrument.smua.OUTPUT_ON  
    time.sleep(keithley_settle_time)

    logging.info("start measurement")
    time_ref = time.time()
    
    # nexp

    # write
    logging.info("configure w2, gate for writing")
    dwf.FDwfAnalogOutEnableSet(hdwf, c_int(w2_ch_gate), 1) 
    dwf.FDwfAnalogOutFunctionSet(hdwf, c_int(w2_ch_gate), dwfconstants.funcDC)
    dwf.FDwfAnalogOutOffsetSet(hdwf, c_int(w2_ch_gate), c_double(gate_voltage))
    # FDwfAnalogOutConfigure(HDWF hdwf, int idxChannel, int fStart)
    # fStart – Start the instrument: 0 stop, 1 start, 3 apply.
    dwf.FDwfAnalogOutConfigure(hdwf, c_int(w2_ch_gate), c_int(0))
    time.sleep(ad3_settle_time)
    dwf.FDwfAnalogOutConfigure(hdwf, c_int(w2_ch_gate), c_int(1))
    time.sleep(ad3_settle_time)

    for idx_exp in range(0, nexp):
        # read
        # set voltage on drain, configure wave gen for reading and start -> wait to be stable, AD3
        logging.info("configure w1_drain, drain for reading")
        dwf.FDwfAnalogOutEnableSet(hdwf, c_int(w1_ch_drain), 1) 
        dwf.FDwfAnalogOutFunctionSet(hdwf, c_int(w1_ch_drain), dwfconstants.funcDC)
        dwf.FDwfAnalogOutOffsetSet(hdwf, c_int(w1_ch_drain), c_double(drain_voltage))
        # FDwfAnalogOutConfigure(HDWF hdwf, int idxChannel, int fStart)
        # fStart – Start the instrument: 0 stop, 1 start, 3 apply.
        dwf.FDwfAnalogOutConfigure(hdwf, c_int(w1_ch_drain), c_int(0))
        time.sleep(ad3_settle_time)
        dwf.FDwfAnalogOutConfigure(hdwf, c_int(w1_ch_drain), c_int(1))
        time.sleep(ad3_settle_time)

        # close the read switch (Y0)
                # Y0 configure
        arduino_board.digital[arduino_bin_mux_s0].write(0)
        arduino_board.digital[arduino_bin_mux_s1].write(0)
        arduino_board.digital[arduino_bin_mux_s2].write(0)
                # close switch
        arduino_board.digital[arduino_bin_mux_enable].write(0)
        time.sleep(sw_settle_time)

        # while loop for reading period with SMUA -> save to file
        start_time = time.time()
        current_time = time.time()
        while (current_time - start_time) < read_duration:
            try:
                measured_i_channel = keithley_instrument.smua.measure.i()
                        # record to file
                with open(file_path, 'a') as file: 
                                    # NOTICE: THE WHILE LOOP/ FOR LOOP INSIDE -> NO CONSTANT UPDATE TO FILE AT ALL -> NO ANIMATION
                    file_writer = csv.DictWriter(file, fieldnames=field_names)
                    info = {
                            'time': time.time() - time_ref,
                            'i_channel': measured_i_channel
                            }
                    file_writer.writerow(info)
                    
            except Exception as CatchError:
                logging.info("ERROR: keithley measure function error")
                logging.info(f"{CatchError=}")
                    
            current_time = time.time()

        time.sleep(0.5)
        # open the read switch
        arduino_board.digital[arduino_bin_mux_enable].write(1)
        # set the drain voltage to 0
        dwf.FDwfAnalogOutOffsetSet(hdwf, c_int(w1_ch_drain), c_double(0))
        dwf.FDwfAnalogOutConfigure(hdwf, c_int(w1_ch_drain), c_int(3))


        # wait between read and write
        time.sleep(wait_between_read_and_write)

        # write
        logging.info("configure w1_drain, drain for writing")
        dwf.FDwfAnalogOutNodeEnableSet(hdwf, c_int(w1_ch_drain), dwfconstants.AnalogOutNodeCarrier, c_int(1))
        dwf.FDwfAnalogOutNodeFunctionSet(hdwf, c_int(w1_ch_drain), dwfconstants.AnalogOutNodeCarrier, dwfconstants.funcPulse)
        dwf.FDwfAnalogOutNodeFrequencySet(hdwf, c_int(w1_ch_drain), dwfconstants.AnalogOutNodeCarrier, c_double(w1_freq))
        # FDwfAnalogOutNodeSymmetrySet(HDWF hdwf, int idxChannel, AnalogOutNode node, double percentageSymmetry)
        dwf.FDwfAnalogOutNodeSymmetrySet(hdwf, c_int(w1_ch_drain), dwfconstants.AnalogOutNodeCarrier, c_double(w1_percentageSymmetry))
        dwf.FDwfAnalogOutOffsetSet(hdwf, w1_ch_drain, c_double(w1_offset))
        dwf.FDwfAnalogOutNodeAmplitudeSet(hdwf, c_int(w1_ch_drain), dwfconstants.AnalogOutNodeCarrier, c_double(w1_amplitude))
        # FDwfAnalogOutRunSet(HDWF hdwf, int idxChannel, double secRun)
        secRun = w1_period
        dwf.FDwfAnalogOutRunSet(hdwf, c_int(w1_ch_drain), c_double(secRun))
        # FDwfAnalogOutRepeatSet(HDWF hdwf, int idxChannel, int cRepeat);
        cRepeat = n_write_cycle
        dwf.FDwfAnalogOutRepeatSet(hdwf, c_int(w1_ch_drain), c_int(cRepeat))
        idle = dwfconstants.DwfAnalogOutIdleOffset
        dwf.FDwfAnalogOutIdleSet(hdwf, c_int(w1_ch_drain), idle)
        # FDwfAnalogOutTriggerSourceSet(HDWF hdwf, int idxChannel, TRIGSRC trigsrc)
        trgsrc = dwfconstants.trigsrcNone
        dwf.FDwfAnalogOutTriggerSourceSet(hdwf, c_int(w1_ch_drain), trgsrc)
        # apply the configuration
        dwf.FDwfAnalogOutConfigure(hdwf, c_int(w1_ch_drain), c_int(0))
        time.sleep(ad3_settle_time)

        # close the write switch
        # y1 for write
        arduino_board.digital[arduino_bin_mux_s0].write(1)
        arduino_board.digital[arduino_bin_mux_s1].write(0)
        arduino_board.digital[arduino_bin_mux_s2].write(0)
        # close switch
        arduino_board.digital[arduino_bin_mux_enable].write(0)
        time.sleep(sw_settle_time)

        # start AD3 wavegen (W2)
        dwf.FDwfAnalogOutConfigure(hdwf, c_int(w1_ch_drain), c_int(1))

        # wait until the AD3 finish
        sts = c_ubyte()
        wavegen_done = dwfconstants.DwfStateDone
        while sts.value != wavegen_done.value:
            dwf.FDwfAnalogOutStatus(hdwf, c_int(w1_ch_drain), byref(sts))
            time.sleep(0.5)
            logging.info(f"{sts=}")
            logging.info(f"{wavegen_done=}")
        
        time.sleep(0.5)
        # open the write switch
        arduino_board.digital[arduino_bin_mux_enable].write(1)

        # wait between exp
        time.sleep(wait_between_exp)

except KeyboardInterrupt:
        # # ======
        # # Open all switches
        # # ======
    logging.info("Keithley measurement    : EXIT")
            # disconnect
    arduino_board.digital[arduino_bin_mux_enable].write(1)
            # turn off the keithley
    keithley_instrument.smua.source.output = keithley_instrument.smua.OUTPUT_OFF   # turn off SMUA
            # AD3 close and reset
    dwf.FDwfAnalogOutReset(hdwf, c_int(w2_ch_gate))
    dwf.FDwfAnalogOutReset(hdwf, c_int(w1_ch_drain))
    dwf.FDwfDeviceCloseAll()
