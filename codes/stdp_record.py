"""
   DWF Python Example
   Author:  Digilent, Inc.
   Modified: Tran Le Phuong Lan
   Revision:  2025-06-16

   Reference: https://forum.digilent.com/topic/23122-lost-and-corrupted-data-analog-discovery-pro/

   Requires:                       
       Python 2.7, 3
"""
from ctypes import *
import sys
import os
from os import sep
import logging
import threading
import pandas as pd
import csv

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

import math
import time
import numpy as np

def record (recordfreq, res, file_path, stop):
    # recordfreq: record frequency [Hz]
    # res: resistor for current measurement [Ohm]
    # stop: signal for the function

    global dwf, hdwf
    # record using 2 osc channels:
        # osc_1 : measure current
        # osc_2 : measure Vds of OECT
    
            # ======
            # Prepare record file
            # ======
    field_names = ['time', 'i', 'v']
    with open(file_path, 'w') as file:
        file_writer = csv.DictWriter(file, fieldnames=field_names)
        file_writer.writeheader()
    
    # This is the PC buffer (or recorded file in the computer).
    # It is TOTALLY DIFFERENT FROM the internal buffer (of the FPGA, which is around 32K samples) 
    # of the analog-in channels of the Analog Device 3.
    # The PC buffer limit only decided by the available disk space in PC, which this code is run.
    # nSamples = 500# 2000000
    cAvailable = c_int()
    cLost = c_int()
    cCorrupted = c_int()
    fLost = 0
    fCorrupted = 0

    #set up acquisition (channel 1 + 2)
    dwf.FDwfAnalogInChannelEnableSet(hdwf, c_int(0), c_int(1))
    dwf.FDwfAnalogInChannelEnableSet(hdwf, c_int(1), c_int(1))
    
    dwf.FDwfAnalogInChannelRangeSet(hdwf, c_int(0), c_double(5))
    dwf.FDwfAnalogInChannelRangeSet(hdwf, c_int(1), c_double(5))
    
    dwf.FDwfAnalogInAcquisitionModeSet(hdwf, dwfconstants.acqmodeRecord)
    dwf.FDwfAnalogInFrequencySet(hdwf, recordfreq)
    dwf.FDwfAnalogInRecordLengthSet(hdwf, c_double(-1)) # c_double(nSamples/hzAcq.value), -1 infinite record length 
    dwf.FDwfAnalogInConfigure(hdwf, c_int(1), c_int(0))


    #wait at least 2 seconds for the offset to stabilize
    time.sleep(2)

    logging.info(f"Starting oscilloscope")
    dwf.FDwfAnalogInConfigure(hdwf, c_int(0), c_int(1))

    cSamples = 0
    sample_idx = 0
    time_step = 1/recordfreq # [s]
    while True:
        dwf.FDwfAnalogInStatus(hdwf, c_int(1), byref(sts))
        if cSamples == 0 and (sts == dwfconstants.DwfStateConfig or sts == dwfconstants.DwfStatePrefill or sts == dwfconstants.DwfStateArmed) :
            logging.info(f"Acquisition not yet started")
            # Acquisition not yet started.
            continue

        dwf.FDwfAnalogInStatusRecord(hdwf, byref(cAvailable), byref(cLost), byref(cCorrupted))
        
        cSamples += cLost.value

        if cLost.value :
            fLost = 1
        if cCorrupted.value :
            fCorrupted = 1

        if cAvailable.value==0 :
            continue
        
        n_samples = cAvailable.value
        logging.info(f"OSC, {cAvailable.value=}")
        rgdSamples1 = (c_double*n_samples)()
        rgdSamples2 = (c_double*n_samples)()

        dwf.FDwfAnalogInStatusData(hdwf, c_int(0), byref(rgdSamples1), cAvailable) # get channel 1: current
        dwf.FDwfAnalogInStatusData(hdwf, c_int(1), byref(rgdSamples2), cAvailable) # get channel 2: voltage
        cSamples += cAvailable.value

        logging.info(f"OSC, {list(rgdSamples1)=}")
            # record to file
        # with open(file_path, 'a') as file: 
        #         # NOTICE: THE WHILE LOOP/ FOR LOOP INSIDE -> NO CONSTANT UPDATE TO FILE AT ALL -> NO ANIMATION
        #         file_writer = csv.DictWriter(file, fieldnames=field_names)
        #         for i in range(0, n_samples):
        #             info = {
        #                         'time': sample_idx * time_step,
        #                         'i': rgdSamples1[i]/res,
        #                         'v': rgdSamples2[i]
        #             }
        #             sample_idx = sample_idx + 1
        #             file_writer.writerow(info)
    
        # time.sleep(0.1)

            # stop the recording process
        if stop():
            logging.info(f"oscillocope, lost    : {cSamples=}")
            logging.info(f"oscillocope, lost    : {fLost=}")
            logging.info(f"oscillocope, corrupt    : {fCorrupted=}")
            break

    logging.info("oscilloscope    : EXIT")
    return

def wavegen (signal_freq, stop):
    # signal_freq: [Hz]

    global dwf, hdwf
        # parameters
    out_ch_1 = c_int(0)
    w1_amplitude = -200e-3 # [V]
    w1_offset = 0 # [V]
    percentageSymmetry = 50
    secRun = 1* (1/signal_freq) # [s], 1 period only
    
    out_ch_2 = c_int(1)
    w2_amplitude = 200e-3 # [V]
    w2_offset = 0 # [V]

    rest_time = 1 # [s]

    logging.info("generate signals")

    logging.info("configure w1")
    dwf.FDwfAnalogOutNodeEnableSet(hdwf, out_ch_1, dwfconstants.AnalogOutNodeCarrier, c_int(1))
    dwf.FDwfAnalogOutNodeFunctionSet(hdwf, out_ch_1, dwfconstants.AnalogOutNodeCarrier, dwfconstants.funcPulse)
    dwf.FDwfAnalogOutNodeFrequencySet(hdwf, out_ch_1, dwfconstants.AnalogOutNodeCarrier, c_double(signal_freq))
    # FDwfAnalogOutNodeSymmetrySet(HDWF hdwf, int idxChannel, AnalogOutNode node, double percentageSymmetry)
    dwf.FDwfAnalogOutNodeSymmetrySet(hdwf, out_ch_1, dwfconstants.AnalogOutNodeCarrier, c_double(percentageSymmetry))
    dwf.FDwfAnalogOutOffsetSet(hdwf, out_ch_1, c_double(w1_offset))
    dwf.FDwfAnalogOutNodeAmplitudeSet(hdwf, out_ch_1, dwfconstants.AnalogOutNodeCarrier, c_double(w1_amplitude))
    # FDwfAnalogOutRunSet(HDWF hdwf, int idxChannel, double secRun)
    dwf.FDwfAnalogOutRunSet(hdwf, out_ch_1, c_double(secRun))
    # FDwfAnalogOutRepeatSet(HDWF hdwf, int idxChannel, int cRepeat);
    dwf.FDwfAnalogOutRepeatSet(hdwf, out_ch_1, c_int(1))
    idle = dwfconstants.DwfAnalogOutIdleOffset
    dwf.FDwfAnalogOutIdleSet(hdwf, out_ch_1, idle)

    logging.info("configure w2")
    dwf.FDwfAnalogOutNodeEnableSet(hdwf, out_ch_2, dwfconstants.AnalogOutNodeCarrier, c_int(1))
    dwf.FDwfAnalogOutNodeFunctionSet(hdwf, out_ch_2, dwfconstants.AnalogOutNodeCarrier, dwfconstants.funcSquare)
    dwf.FDwfAnalogOutNodeFrequencySet(hdwf, out_ch_2, dwfconstants.AnalogOutNodeCarrier, c_double(signal_freq))
    # FDwfAnalogOutNodeSymmetrySet(HDWF hdwf, int idxChannel, AnalogOutNode node, double percentageSymmetry)
    dwf.FDwfAnalogOutNodeSymmetrySet(hdwf, out_ch_2, dwfconstants.AnalogOutNodeCarrier, c_double(percentageSymmetry))
    dwf.FDwfAnalogOutOffsetSet(hdwf, out_ch_2, c_double(w2_offset))
    dwf.FDwfAnalogOutNodeAmplitudeSet(hdwf, out_ch_2, dwfconstants.AnalogOutNodeCarrier, c_double(w2_amplitude))
    # FDwfAnalogOutRunSet(HDWF hdwf, int idxChannel, double secRun)
    dwf.FDwfAnalogOutRunSet(hdwf, out_ch_2, c_double(secRun))
    # FDwfAnalogOutRepeatSet(HDWF hdwf, int idxChannel, int cRepeat);
    dwf.FDwfAnalogOutRepeatSet(hdwf, out_ch_2, c_int(1))
    idle = dwfconstants.DwfAnalogOutIdleOffset
    dwf.FDwfAnalogOutIdleSet(hdwf, out_ch_2, idle)
    # # FDwfAnalogOutTriggerSourceSet(HDWF hdwf, int idxChannel, TRIGSRC trigsrc)
    # trgsrc = dwfconstants.trigsrcAnalogOut1
    # dwf.FDwfAnalogOutTriggerSourceSet(hdwf, out_ch_2, trgsrc)

    logging.info("start the wavegen")
    while True:
        # FDwfAnalogOutConfigure(HDWF hdwf, int idxChannel, int fStart)
        dwf.FDwfAnalogOutConfigure(hdwf, out_ch_1, c_int(1))
        time.sleep(secRun)
        dwf.FDwfAnalogOutConfigure(hdwf, out_ch_2, c_int(1))
        
        time.sleep(rest_time)
        
        if stop():
            # stop all channels
            dwf.FDwfAnalogOutConfigure(hdwf, -1, c_int(0))
            break
    
    logging.info("wavegen: EXIT")
    return

if __name__ == "__main__":


    #declare ctype variables
    hdwf = c_int()
    sts = c_byte()
    
    #print(DWF version
    version = create_string_buffer(16)
    dwf.FDwfGetVersion(version)
    print("DWF Version: "+str(version.value))

    #open device
    print("Opening first device")
    dwf.FDwfDeviceOpen(c_int(-1), byref(hdwf))

    if hdwf.value == dwfconstants.hdwfNone.value:
        szerr = create_string_buffer(512)
        dwf.FDwfGetLastErrorMsg(szerr)
        print(str(szerr.value))
        print("failed to open device")
        quit()

    dwf.FDwfDeviceAutoConfigureSet(hdwf, c_int(0)) # 0 = the device will only be configured when FDwf###Configure is called

    
    # init logger
    format = "%(asctime)s: %(message)s"
    log_file_path = 'example.log'
    logging.basicConfig(format=format, level=logging.INFO,  
                        datefmt="%H:%M:%S", filename= log_file_path, filemode= 'w')

    logging.info("Main    : Prepare measurement")

    stop_gen_threads = False
    signal_freq = 2 # [Hz]
    # xgen = threading.Thread(target=wavegen, daemon=True, args=(signal_freq, lambda: stop_gen_threads, ))
    xgen = threading.Thread(target=wavegen, daemon=True, args=(signal_freq, lambda: stop_gen_threads, ))

    stop_osc_threads = False
    rec_freq = 200 # [Hz]
    # Resistor for current measurement (res)
    R = 0.00205806419e+3 # Ohm
    file_path = "C:/Users/20245580/LabCode/Codes_For_Experiments/exp_data/20250616/stdp.csv"
    xosc = threading.Thread(target=record, daemon=True, args=(rec_freq, R, file_path, lambda: stop_osc_threads, ))

    logging.info("Main    : Run measurement")
    xosc.start()
    time.sleep(2)
    xgen.start()

    while True:
        logging.info("Main    : inside")
        time.sleep(1)

    # while True:
        
    #      print(f"input 'stop_gen', 'stop_osc', then 'stop_main':  ")
    #      input_str = str(input())

    #      match input_str:
    #             case "stop_gen":
    #                 stop_gen_threads = True
    #                 time.sleep(3)
    #             case "stop_osc":
    #                 stop_osc_threads = True
    #                 time.sleep(3)
    #             case "stop_main":
    #                 if (stop_gen_threads == True) and (stop_osc_threads==True):
    #                     dwf.FDwfDeviceCloseAll()
    #                     break
    #                 else:
    #                      pass
    
    # logging.info("Main    : EXIT")
