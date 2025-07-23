"""
    Analog Discover 3 (AD3) and Rigol Ds1054 Oscilloscope
    Trigger on wave signals of AD3 and measure from Rigol scope
    Author:  Tran Le Phuong Lan.
    Created:  2025-07-23

    Requires:                       
       Python 2.7, 3
       SDK for AD3
       NI-VISA
       pyvisa
       pyusb
    Reference:

    [1] [Rigol Ds1054 code examples](https://github.com/LaN-Tran/Automate_Lab_Instrument/blob/main/20250722/oscilloscope_rigolds1054.ipynb)
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
    # # Connect and prepare the Rigol osc
    # # ======
rm = pyvisa.ResourceManager('C:/windows/System32/visa64.dll')
osc_rig = rm.open_resource('USB0::0x1AB1::0x04CE::DS1ZA221403528::INSTR')
osc_rig.timeout = 1500 # [ms]
# osc_rig.chunk_size = 32

    # # ======
    # # Record file
    # # ======
        # path to the measurement record
file_path = "C:/Users/20245580/LabCode/Codes_For_Experiments/exp_data/20250723/"
field_names = ['time', 'volts']

try:
        # # ======
        # # Run osc, configure
        # # ======

        # run osc
        # -------
    osc_rig.write(':RUN')

        # configure for collecting data
        # -------
        # set the waveform mode to RAW to read the data from the internal memory instead
    osc_rig.write(':WAV:MODE RAW')
        # set the waveform format
    osc_rig.write(':WAV:FORM BYTE') # :WAV:DATA? max 250000
        # check the setup
    logging.info(f"osc: {osc_rig.query(':WAV:MODE?')=}")
    logging.info(f"osc: {osc_rig.query(':WAV:FORM?')=}")
        # set the channel where the data is collected
    osc_rig.write(':WAV:SOUR CHAN1')
    logging.info(f"osc: {osc_rig.query(':WAV:SOUR?')}")
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
    # check, and read-in the current internal memory depth
    mem_depth = osc_rig.query(':ACQ:MDEP?')
    mem_depth = int(mem_depth) 
    logging.info(f"osc: {mem_depth=}")

    # and < 250000.
    samples_in_a_batch = 150000

    # How many times attempting to repeat :WAV:DATA if it fails
    n_retries = 10

    # process the data and plot
    # convert values to display the right value 
    # and plot

    # X-axis conversion
    sampling_rate = osc_rig.query(':ACQ:SRATE?') # samples/second or points/second
    sampling_rate = float(sampling_rate)
    logging.info(f"osc: {sampling_rate=}")

    # can not do the readout to make the y-axis conversion here
    # it makes everything wrong
    # must do it only after the osc is stop after finishing a single scan mode.

    # set single capture
    osc_rig.write(':SING')
    time.sleep(0.3) # wait for osc transition from RUN -> SINGLE

        # # ======
        # # Measurement parameter
        # # ======
    logging.info("Main    : Prepare measurement")

    sw_settle_time = 0.1 # [s]
    keithley_settle_time = 0.5 # [s]
    read_duration = 1 # [s]
    wait_between_read_and_write = 2 # [s]
    nexp = 3
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
    delta_tpre_tpost = 60e-3 # [s]
    n_write_cycle = 5

    w1_ch_drain = 0 # 
    w1_period = 0.5 # [s]
    w1_pulse_width = 50e-3 # [s]
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


    logging.info("start measurement")
    time_ref = time.time()
    
    # nexp
    for idx_exp in range(0, nexp):
        logging.info(f"{idx_exp=}")
        # read
        # set voltage on drain, configure wave gen for reading and start -> wait to be stable, AD3
        logging.info("configure w1_drain, drain for reading")
        dwf.FDwfAnalogOutEnableSet(hdwf, c_int(w1_ch_drain), 1) 
        dwf.FDwfAnalogOutFunctionSet(hdwf, c_int(w1_ch_drain), dwfconstants.funcDC)
        dwf.FDwfAnalogOutOffsetSet(hdwf, c_int(w1_ch_drain), c_double(drain_voltage))
        # FDwfAnalogOutConfigure(HDWF hdwf, int idxChannel, int fStart)
        # fStart – Start the instrument: 0 stop, 1 start, 3 apply.
        dwf.FDwfAnalogOutConfigure(hdwf, c_int(w1_ch_drain), 3)
        time.sleep(ad3_settle_time)
        dwf.FDwfAnalogOutConfigure(hdwf, c_int(w1_ch_drain), 1)

    
        # while loop for reading period with SMUA -> save to file
        start_time = time.time()
        current_time = time.time()
        while (current_time - start_time) < read_duration:
            try:
                logging.info("reading..")    
            except Exception as CatchError:
                logging.info("ERROR: keithley measure function error")
                logging.info(f"{CatchError=}")
                    
            current_time = time.time()
        
        # stop the drain voltage
        dwf.FDwfAnalogOutConfigure(hdwf, c_int(w1_ch_drain), 0)
        
        # wait between read and write
        time.sleep(wait_between_read_and_write)

        # write
        # configure the AD3 wavegen configure (W1, W2) -> apply and stop 
        logging.info("configure w1, drain for writing")
        dwf.FDwfAnalogOutNodeEnableSet(hdwf, w1_ch_drain, dwfconstants.AnalogOutNodeCarrier, c_int(1))
        dwf.FDwfAnalogOutNodeFunctionSet(hdwf, w1_ch_drain, dwfconstants.AnalogOutNodeCarrier, dwfconstants.funcPulse)
        # set freq for the customed signal
        dwf.FDwfAnalogOutNodeFrequencySet(hdwf, w1_ch_drain, dwfconstants.AnalogOutNodeCarrier, c_double(w1_freq))
        # FDwfAnalogOutNodeSymmetrySet(HDWF hdwf, int idxChannel, AnalogOutNode node, double percentageSymmetry)
        dwf.FDwfAnalogOutNodeSymmetrySet(hdwf, w1_ch_drain, dwfconstants.AnalogOutNodeCarrier, c_double(w1_percentageSymmetry))
        dwf.FDwfAnalogOutOffsetSet(hdwf, w1_ch_drain, c_double(w1_offset))
        dwf.FDwfAnalogOutNodeAmplitudeSet(hdwf, w1_ch_drain, dwfconstants.AnalogOutNodeCarrier, c_double(w1_amplitude))

        # FDwfAnalogOutRunSet(HDWF hdwf, int idxChannel, double secRun)
        secRun =  w1_period # determine the 1 period of the signal
        dwf.FDwfAnalogOutRunSet(hdwf, w1_ch_drain, c_double(secRun))
        # FDwfAnalogOutWaitSet(HDWF hdwf, int idxChannel, double secWait)
        dwf.FDwfAnalogOutWaitSet(hdwf, w1_ch_drain, c_double(secWait_1))
        # FDwfAnalogOutRepeatSet(HDWF hdwf, int idxChannel, int cRepeat);
        cRepeat= n_write_cycle # how many periods 
        dwf.FDwfAnalogOutRepeatSet(hdwf, w1_ch_drain, c_int(cRepeat))
        idle = dwfconstants.DwfAnalogOutIdleOffset
        dwf.FDwfAnalogOutIdleSet(hdwf, w1_ch_drain, idle)
        # apply the configuration
        # FDwfAnalogOutConfigure(HDWF hdwf, int idxChannel, int fStart)
        # fStart – Start the instrument: 0 stop, 1 start, 3 apply.
        dwf.FDwfAnalogOutConfigure(hdwf, w1_ch_drain, c_int(0))

        logging.info("configure w2, gate for writing")
        dwf.FDwfAnalogOutNodeEnableSet(hdwf, w2_ch_gate, dwfconstants.AnalogOutNodeCarrier, c_int(1))
        dwf.FDwfAnalogOutNodeFunctionSet(hdwf, w2_ch_gate, dwfconstants.AnalogOutNodeCarrier, dwfconstants.funcPulse)
        dwf.FDwfAnalogOutNodeFrequencySet(hdwf, w2_ch_gate, dwfconstants.AnalogOutNodeCarrier, c_double(w2_freq))
        # FDwfAnalogOutNodeSymmetrySet(HDWF hdwf, int idxChannel, AnalogOutNode node, double percentageSymmetry)
        dwf.FDwfAnalogOutNodeSymmetrySet(hdwf, w2_ch_gate, dwfconstants.AnalogOutNodeCarrier, c_double(w2_percentageSymmetry))
        dwf.FDwfAnalogOutOffsetSet(hdwf, w2_ch_gate, c_double(w2_offset))
        dwf.FDwfAnalogOutNodeAmplitudeSet(hdwf, w2_ch_gate, dwfconstants.AnalogOutNodeCarrier, c_double(w2_amplitude))
        # FDwfAnalogOutRunSet(HDWF hdwf, int idxChannel, double secRun)
        secRun = w2_period
        dwf.FDwfAnalogOutRunSet(hdwf, w2_ch_gate, c_double(secRun))
        # FDwfAnalogOutRepeatSet(HDWF hdwf, int idxChannel, int cRepeat);
        dwf.FDwfAnalogOutRepeatSet(hdwf, w2_ch_gate, c_int(cRepeat))
        idle = dwfconstants.DwfAnalogOutIdleOffset
        dwf.FDwfAnalogOutIdleSet(hdwf, w2_ch_gate, idle)
        # FDwfAnalogOutTriggerSourceSet(HDWF hdwf, int idxChannel, TRIGSRC trigsrc)
        trgsrc = dwfconstants.trigsrcAnalogOut1
        dwf.FDwfAnalogOutTriggerSourceSet(hdwf, w2_ch_gate, trgsrc)
        # FDwfAnalogOutTriggerSlopeSet(HDWF hdwf, int idxChannel, DwfTriggerSlope slope)
        slope = dwfconstants.DwfTriggerSlopeRise
        dwf.FDwfAnalogOutTriggerSlopeSet(hdwf, w2_ch_gate, slope)
        dwf.FDwfAnalogOutWaitSet(hdwf, w2_ch_gate, c_double(secWait_2))
        # apply the configuration
        dwf.FDwfAnalogOutConfigure(hdwf, w2_ch_gate, c_int(0))

        # start AD3 wavegen (W1, W2)
        dwf.FDwfAnalogOutConfigure(hdwf, w2_ch_gate, c_int(1))
        time.sleep(1)
        dwf.FDwfAnalogOutConfigure(hdwf, w1_ch_drain, c_int(1))

        # wait until the AD3 finish
        sts = c_ubyte()
        wavegen_done = dwfconstants.DwfStateDone
        while sts.value != wavegen_done.value:
            dwf.FDwfAnalogOutStatus(hdwf, w2_ch_gate, byref(sts))
            time.sleep(0.5)
            logging.info(f"{sts=}")
            logging.info(f"{wavegen_done=}")
        
        # OSC
        # check whether there is data to collect and save it to file
        trigger_sts = osc_rig.query(':TRIG:STAT?')
        logging.info(f"osc: {trigger_sts=}")
        if 'STOP' in trigger_sts:
            # if trigger is stopped, collect the data from the internal memory
            buf = []
            idx_batch = 0
            len_buf = len(buf)
            while len_buf < mem_depth:
                start= idx_batch*samples_in_a_batch + 1
                stop = start + samples_in_a_batch - 1
                stop = mem_depth if stop > mem_depth else stop

                time.sleep(0.01)
                osc_rig.write(f':WAV:STAR {start}')
                osc_rig.write(f':WAV:STOP {stop}')

                for i_retry in range(0, n_retries):
                    try:
                        tmp = osc_rig.query_binary_values(':WAV:DATA?', datatype='B')
                        break
                    except Exception as e:
                        logging.info(f"osc: {e=}")

                buf += tmp

                len_buf = len(buf)
                logging.info(f"osc: {len_buf=}") 
                idx_batch = idx_batch + 1    
            
            time_axis = np.arange(0, len(buf)) / sampling_rate
            np_buf = np.array(buf) 
            # Y-axis conversion
            yorigin = osc_rig.query(':WAV:YORigin?')
            yorigin = float(yorigin)
            logging.info(f"osc: {yorigin=}")

            yref = osc_rig.query(':WAV:YREFerence?')
            yref = float(yref)
            logging.info(f"osc: {yref=}")

            yincr = osc_rig.query(':WAV:YINCrement?')
            yincr = float(yincr)
            logging.info(f"osc: {yincr=}")
            
            # print(f"{yorigin=}, {yref=}, {yincr=}")
            volt_axis = (np_buf - yorigin - yref)*yincr
            

            # save to file
            file_path_trace = file_path + 'trace_' + str(idx_exp) +'.csv'
            
            with open(file_path_trace, 'w') as file: 
                        # NOTICE: THE WHILE LOOP/ FOR LOOP INSIDE -> NO CONSTANT UPDATE TO FILE AT ALL -> NO ANIMATION
                file_writer = csv.DictWriter(file, fieldnames=field_names)
                file_writer.writeheader()
                for i in range(0, len(time_axis)):
                        info = {
                                'time': time_axis[i],
                                'volts': volt_axis[i]
                                        # 'i_gate': measured_i_gate,
                                                        }
                        file_writer.writerow(info)

            logging.info(f"finish saving osc data to .csv")
            osc_rig.write(':RUN')
            osc_rig.write(':SING')

        # wait between exp
        time.sleep(wait_between_exp)

except KeyboardInterrupt:
        # # ======
        # # Open all switches
        # # ======
    logging.info("AD3    : EXIT")
            # disconnect
    dwf.FDwfAnalogOutReset(hdwf, c_int(0))
    dwf.FDwfDeviceCloseAll()

    logging.info("OSC    : STOP")
    osc_rig.write(':STOP')

