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

def record_configure (recordfreq):

    global dwf, hdwf
    # record using 2 osc channels:
        # osc_1 : measure current
        # osc_2 : measure Vds of OECT

        #set up acquisition (channel 1 + 2)
    dwf.FDwfAnalogInChannelEnableSet(hdwf, c_int(0), c_int(1))
    dwf.FDwfAnalogInChannelEnableSet(hdwf, c_int(1), c_int(1))
    
    dwf.FDwfAnalogInChannelRangeSet(hdwf, c_int(0), c_double(5))
    dwf.FDwfAnalogInChannelRangeSet(hdwf, c_int(1), c_double(5))
    
    dwf.FDwfAnalogInAcquisitionModeSet(hdwf, dwfconstants.acqmodeRecord)
    dwf.FDwfAnalogInFrequencySet(hdwf, recordfreq)
    dwf.FDwfAnalogInRecordLengthSet(hdwf, c_double(-1)) # c_double(nSamples/hzAcq.value), -1 infinite record length 
    
    # apply the osc configuration
    dwf.FDwfAnalogInConfigure(hdwf, c_int(1), c_int(0))
    #wait at least 2 seconds for the offset to stabilize
    time.sleep(2)

    return

def wavegen_configure ():

    global dwf, hdwf
        # parameters

    out_ch_1 = c_int(0)
    w1_freq = 1 # [Hz]
    w1_amplitude = -200e-3 # [V]
    w1_offset = 0 # [V]
    w1_percentageSymmetry = 50 # [%]
    
    
    out_ch_2 = c_int(1)
    w2_freq = 1 # [Hz]
    w2_amplitude = 200e-3 # [V]
    w2_offset = 0 # [V]
    w2_percentageSymmetry = 50

    delta_tpre_tpost = 100e-3 # [s]
    rest_time = 2 # [s]

    logging.info("generate signals")

    logging.info("configure w1")
    dwf.FDwfAnalogOutNodeEnableSet(hdwf, out_ch_1, dwfconstants.AnalogOutNodeCarrier, c_int(1))
    dwf.FDwfAnalogOutNodeFunctionSet(hdwf, out_ch_1, dwfconstants.AnalogOutNodeCarrier, dwfconstants.funcPulse)
    dwf.FDwfAnalogOutNodeFrequencySet(hdwf, out_ch_1, dwfconstants.AnalogOutNodeCarrier, c_double(w1_freq))
        # FDwfAnalogOutNodeSymmetrySet(HDWF hdwf, int idxChannel, AnalogOutNode node, double percentageSymmetry)
    dwf.FDwfAnalogOutNodeSymmetrySet(hdwf, out_ch_1, dwfconstants.AnalogOutNodeCarrier, c_double(w1_percentageSymmetry))
    dwf.FDwfAnalogOutOffsetSet(hdwf, out_ch_1, c_double(w1_offset))
    dwf.FDwfAnalogOutNodeAmplitudeSet(hdwf, out_ch_1, dwfconstants.AnalogOutNodeCarrier, c_double(w1_amplitude))
        # FDwfAnalogOutTriggerSourceSet(HDWF hdwf, int idxChannel, TRIGSRC trigsrc)
    trgsrc = dwfconstants.trigsrcNone
    dwf.FDwfAnalogOutTriggerSourceSet(hdwf, out_ch_1, trgsrc)
        # FDwfAnalogOutRunSet(HDWF hdwf, int idxChannel, double secRun)
    secRun = 1* (1/w1_freq) # [s], 1 period only
    dwf.FDwfAnalogOutRunSet(hdwf, out_ch_1, c_double(secRun))
        # FDwfAnalogOutWaitSet(HDWF hdwf, int idxChannel, double secWait)
    secWait = 2 # [s]
    dwf.FDwfAnalogOutWaitSet(hdwf, out_ch_1, c_double(secWait))
        # FDwfAnalogOutRepeatSet(HDWF hdwf, int idxChannel, int cRepeat);
    cRepeat= c_int(100)
    dwf.FDwfAnalogOutRepeatSet(hdwf, out_ch_1, cRepeat)
    idle = dwfconstants.DwfAnalogOutIdleOffset
    dwf.FDwfAnalogOutIdleSet(hdwf, out_ch_1, idle)

    logging.info("configure w2")
    dwf.FDwfAnalogOutNodeEnableSet(hdwf, out_ch_2, dwfconstants.AnalogOutNodeCarrier, c_int(1))
    dwf.FDwfAnalogOutNodeFunctionSet(hdwf, out_ch_2, dwfconstants.AnalogOutNodeCarrier, dwfconstants.funcPulse)
    dwf.FDwfAnalogOutNodeFrequencySet(hdwf, out_ch_2, dwfconstants.AnalogOutNodeCarrier, c_double(w2_freq))
        # FDwfAnalogOutNodeSymmetrySet(HDWF hdwf, int idxChannel, AnalogOutNode node, double percentageSymmetry)
    dwf.FDwfAnalogOutNodeSymmetrySet(hdwf, out_ch_2, dwfconstants.AnalogOutNodeCarrier, c_double(w2_percentageSymmetry))
    dwf.FDwfAnalogOutOffsetSet(hdwf, out_ch_2, c_double(w2_offset))
    dwf.FDwfAnalogOutNodeAmplitudeSet(hdwf, out_ch_2, dwfconstants.AnalogOutNodeCarrier, c_double(w2_amplitude))
        # FDwfAnalogOutRunSet(HDWF hdwf, int idxChannel, double secRun)
    secRun = 1*(1/w2_freq)
    dwf.FDwfAnalogOutRunSet(hdwf, out_ch_2, c_double(secRun))
        # FDwfAnalogOutRepeatSet(HDWF hdwf, int idxChannel, int cRepeat);
    dwf.FDwfAnalogOutRepeatSet(hdwf, out_ch_2, cRepeat)
    idle = dwfconstants.DwfAnalogOutIdleOffset
    dwf.FDwfAnalogOutIdleSet(hdwf, out_ch_2, idle)
        # FDwfAnalogOutTriggerSourceSet(HDWF hdwf, int idxChannel, TRIGSRC trigsrc)
    trgsrc = dwfconstants.trigsrcAnalogOut1
    dwf.FDwfAnalogOutTriggerSourceSet(hdwf, out_ch_2, trgsrc)
        # FDwfAnalogOutTriggerSlopeSet(HDWF hdwf, int idxChannel, DwfTriggerSlope slope)
    slope = dwfconstants.DwfTriggerSlopeRise
    dwf.FDwfAnalogOutTriggerSlopeSet(hdwf, out_ch_2, slope)
    secWait =  (1* (1/w1_freq))/2 +  delta_tpre_tpost # [s]
    dwf.FDwfAnalogOutWaitSet(hdwf, out_ch_2, c_double(secWait))

    logging.info("start the wavegen")
    return



    # init logger
format = "%(asctime)s: %(message)s"
log_file_path = 'example.log'
logging.basicConfig(format=format, level=logging.INFO,  
                        datefmt="%H:%M:%S", filename= log_file_path, filemode= 'w')

file_path = "C:/Users/20245580/LabCode/Codes_For_Experiments/exp_data/20250616/stdp.csv"
        # Prepare record file
field_names = ['time', 'i', 'v']
with open(file_path, 'w') as file:
        file_writer = csv.DictWriter(file, fieldnames=field_names)
        file_writer.writeheader()

        # declare ctype variables
hdwf = c_int()
sts = c_byte()
hzAcq = c_double(200)
    
        # print(DWF version
version = create_string_buffer(16)
dwf.FDwfGetVersion(version)
print("DWF Version: "+str(version.value))

        # open device
print("Opening first device")
dwf.FDwfDeviceOpen(c_int(-1), byref(hdwf))

if hdwf.value == dwfconstants.hdwfNone.value:
    szerr = create_string_buffer(512)
    dwf.FDwfGetLastErrorMsg(szerr)
    print(str(szerr.value))
    print("failed to open device")
    quit()

dwf.FDwfDeviceAutoConfigureSet(hdwf, c_int(0)) # 0 = the device will only be configured when FDwf###Configure is called

wavegen_configure()

rec_freq = 200 # [Hz]
record_configure(rec_freq)
logging.info(f"Starting oscilloscope")
dwf.FDwfAnalogInConfigure(hdwf, c_int(0), c_int(1))

    # start the wavegenerator
dwf.FDwfAnalogOutConfigure(hdwf, -1, c_int(1))

    # Resistor for current measurement (res)
R = 0.00205806419e+3 # Ohm

cAvailable = c_int()
cLost = c_int()
cCorrupted = c_int()
fLost = 0
fCorrupted = 0

cSamples = 0
sample_idx = 0
time_step = 1/rec_freq # [s]
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
    # logging.info(f"OSC, {cAvailable.value=}")
    rgdSamples1 = (c_double*n_samples)()
    rgdSamples2 = (c_double*n_samples)()

    dwf.FDwfAnalogInStatusData(hdwf, c_int(0), byref(rgdSamples1), cAvailable) # get channel 1: current
    dwf.FDwfAnalogInStatusData(hdwf, c_int(1), byref(rgdSamples2), cAvailable) # get channel 2: voltage
    cSamples += cAvailable.value
    logging.info(f"OSC, {list(rgdSamples1)=}")
    logging.info(f"OSC, {list(rgdSamples2)=}")
        #     # record to file
        # with open(file_path, 'a') as file: 
        #         # NOTICE: THE WHILE LOOP/ FOR LOOP INSIDE -> NO CONSTANT UPDATE TO FILE AT ALL -> NO ANIMATION
        #         file_writer = csv.DictWriter(file, fieldnames=field_names)
        #         for i in range(0, n_samples):
        #             info = {
        #                         'time': sample_idx * time_step,
        #                         'i': rgdSamples1[i]/R,
        #                         'v': rgdSamples2[i]
        #             }
        #             sample_idx = sample_idx + 1
        #             file_writer.writerow(info)
    
        # time.sleep(0.1)
