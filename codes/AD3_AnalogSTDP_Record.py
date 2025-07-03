"""
   Analog STDP record 
   Author:  Tran Le Phuong Lan, 
   Refer:  Digilent, Inc.
   Revision:  2025-06-17

   Reference: 
    
    - 1. https://forum.digilent.com/topic/23122-lost-and-corrupted-data-analog-discovery-pro/

    - 2. https://forum.digilent.com/topic/27919-set-the-trigger-on-the-wavegen-channel-2-to-scope-via-the-sdk-in-python/

   Requires:                       
       Python 2.7, 3
"""
from ctypes import *
import sys
import os
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


# from dwfconstants import *
import math
import time
import matplotlib.pyplot as plt
# import sys
import numpy as np

if sys.platform.startswith("win"):
    dwf = cdll.dwf
elif sys.platform.startswith("darwin"):
    dwf = cdll.LoadLibrary("/Library/Frameworks/dwf.framework/dwf")
else:
    dwf = cdll.LoadLibrary("libdwf.so")

import logging
# init logger
format = "%(asctime)s: %(message)s"
log_file_path = 'example.log'
logging.basicConfig(format=format, level=logging.INFO,  
                        datefmt="%H:%M:%S", filename= log_file_path, filemode= 'w')


#declare ctype variables
hdwf = c_int()
sts = c_byte()
hzAcq = c_double(200)
# This is the PC buffer (or recorded file in the computer).
# It is TOTALLY DIFFERENT FROM the internal buffer (of the FPGA, which is around 32K samples) 
# of the analog-in channels of the Analog Device 3.
# The PC buffer limit only decided by the available disk space in PC, which this code is run.
# nSamples = 500# 200000
# rgdSamples = (c_double*nSamples)()
cAvailable = c_int()
cLost = c_int()
cCorrupted = c_int()
fLost = 0
fCorrupted = 0

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

print("Generating sine wave...")
out_ch_1 = c_int(0)
w1_freq = 1 # [Hz]
w1_amplitude = -200e-3 # [V]
w1_offset = 0 # [V]
w1_percentageSymmetry = 10 # [%]
        
out_ch_2 = c_int(1)
w2_freq = 1 # [Hz]
w2_amplitude = -200e-3 # [V]
w2_offset = 0 # [V]
w2_percentageSymmetry = 10

delta_tpre_tpost = 0.1 # [s]

# Resistor for current measurement (res)
R = 0.00205806419e+3 # Ohm

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
secWait = 4 # [s]
dwf.FDwfAnalogOutWaitSet(hdwf, out_ch_1, c_double(secWait))
# FDwfAnalogOutRepeatSet(HDWF hdwf, int idxChannel, int cRepeat);
cRepeat= c_int(5)
dwf.FDwfAnalogOutRepeatSet(hdwf, out_ch_1, cRepeat)
idle = dwfconstants.DwfAnalogOutIdleOffset
dwf.FDwfAnalogOutIdleSet(hdwf, out_ch_1, idle)
# apply the configuration
dwf.FDwfAnalogOutConfigure(hdwf, out_ch_1, c_int(3))

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
cRepeat = 2
dwf.FDwfAnalogOutRepeatSet(hdwf, out_ch_2, cRepeat)
idle = dwfconstants.DwfAnalogOutIdleOffset
dwf.FDwfAnalogOutIdleSet(hdwf, out_ch_2, idle)
# M1 (Not as expected)
# # FDwfAnalogOutTriggerSourceSet(HDWF hdwf, int idxChannel, TRIGSRC trigsrc)
# trgsrc = dwfconstants.trigsrcAnalogOut1
# dwf.FDwfAnalogOutTriggerSourceSet(hdwf, out_ch_2, trgsrc)
# # FDwfAnalogOutTriggerSlopeSet(HDWF hdwf, int idxChannel, DwfTriggerSlope slope)
# slope = dwfconstants.DwfTriggerSlopeRise
# dwf.FDwfAnalogOutTriggerSlopeSet(hdwf, out_ch_2, slope)
# secWait =  (1* (1/w1_freq))/2 +  delta_tpre_tpost # [s]
# dwf.FDwfAnalogOutWaitSet(hdwf, out_ch_2, c_double(secWait))
# M2 (not as expected)
trgsrc = dwfconstants.trigsrcNone
dwf.FDwfAnalogOutTriggerSourceSet(hdwf, out_ch_2, trgsrc)
dwf.FDwfAnalogOutWaitSet(hdwf, out_ch_2, c_double(secWait))
# apply the configuration
dwf.FDwfAnalogOutConfigure(hdwf, out_ch_2, c_int(3))


#set up acquisition (channel 1 + 2)
dwf.FDwfAnalogInChannelEnableSet(hdwf, c_int(0), c_int(1))
dwf.FDwfAnalogInChannelEnableSet(hdwf, c_int(1), c_int(1))
    
dwf.FDwfAnalogInChannelRangeSet(hdwf, c_int(0), c_double(5))
dwf.FDwfAnalogInChannelRangeSet(hdwf, c_int(1), c_double(5))
    
dwf.FDwfAnalogInAcquisitionModeSet(hdwf, dwfconstants.acqmodeRecord)
dwf.FDwfAnalogInFrequencySet(hdwf, hzAcq)
dwf.FDwfAnalogInRecordLengthSet(hdwf, c_double(-1)) # c_double(nSamples/hzAcq.value), -1 infinite record length 
    
# apply the osc configuration
dwf.FDwfAnalogInConfigure(hdwf, c_int(1), c_int(0))
#wait at least 2 seconds for the offset to stabilize
time.sleep(2)

print("Starting oscilloscope")
dwf.FDwfAnalogInConfigure(hdwf, c_int(0), c_int(1))
time.sleep(1)

logging.info("start waves")
# M0 (with this, the channel 2 configured is automatically same as channel 1)
# dwf.FDwfAnalogOutConfigure(hdwf, -1, c_int(1))
# M1 (expected)
# dwf.FDwfAnalogOutConfigure(hdwf, out_ch_2, c_int(1))
# dwf.FDwfAnalogOutConfigure(hdwf, out_ch_1, c_int(1))
# M2 (not as expected)
dwf.FDwfAnalogOutConfigure(hdwf, out_ch_1, c_int(1))
time.sleep(delta_tpre_tpost)
dwf.FDwfAnalogOutConfigure(hdwf, out_ch_2, c_int(1))


import csv
file_path = "C:/Users/20245580/LabCode/Codes_For_Experiments/exp_data/20250616/stdp.csv"
        # Prepare record file
field_names = ['time', 'i', 'v']
with open(file_path, 'w') as file:
    file_writer = csv.DictWriter(file, fieldnames=field_names)
    file_writer.writeheader()

cSamples = 0
print("Press Ctrl+C to stop")
# while cSamples < nSamples:
time_step = 1/hzAcq.value
sample_idx = 0
while True:
    dwf.FDwfAnalogInStatus(hdwf, c_int(1), byref(sts))
    if cSamples == 0 and (sts == dwfconstants.DwfStateConfig or sts == dwfconstants.DwfStatePrefill or sts == dwfconstants.DwfStateArmed) :
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
    
    
    rgdSamples1 = (c_double*cAvailable.value)()
    rgdSamples2 = (c_double*cAvailable.value)()

    dwf.FDwfAnalogInStatusData(hdwf, c_int(0), byref(rgdSamples1), cAvailable) # get channel 1 data
    dwf.FDwfAnalogInStatusData(hdwf, c_int(1), byref(rgdSamples2), cAvailable) # get channel 1 data
    cSamples += cAvailable.value

    list_rgdSamples = list(rgdSamples1)
    list_rgdSamples2 = list(rgdSamples2)
    # print(f"{list_rgdSamples=}") 
    logging.info(f"OSC, {cLost.value=}")
    logging.info(f"OSC, {cCorrupted.value=}")
        # record to file
    with open(file_path, 'a') as file: 
        # NOTICE: THE WHILE LOOP/ FOR LOOP INSIDE -> NO CONSTANT UPDATE TO FILE AT ALL -> NO ANIMATION
        file_writer = csv.DictWriter(file, fieldnames=field_names)
        for i in range(0, len(list_rgdSamples)):
            info = {
                        'time': sample_idx*time_step,
                        'i': list_rgdSamples[i]/R,
                        'v': list_rgdSamples2[i]
                    }
            sample_idx = sample_idx + 1
            file_writer.writerow(info)
    time.sleep(0.01)

dwf.FDwfAnalogOutReset(hdwf, c_int(0))
dwf.FDwfDeviceCloseAll()


