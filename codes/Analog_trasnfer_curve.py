"""
   Analog transfer curve, transistor test
   Author:  Tran Le Phuong Lan
   Modifier: 
   Revision:  2025-06-19

   Requires:                       
       Python 2.7, 3
   
   Reference:
        [1] Physical setup: https://digilent.com/reference/test-and-measurement/guides/waveforms-curve-tracer?srsltid=AfmBOoqN0yxSmK0MYBprgry4HaLvbSzvA-zQUWobe24-F8WjA6Xg2Gkq
"""

from ctypes import *
import time
import sys
from os import sep
import matplotlib.pyplot as plt
import numpy as np
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

from dwfconstants import *

import logging
# init logger
format = "%(asctime)s: %(message)s"
log_file_path = 'example.log'
logging.basicConfig(format=format, level=logging.INFO,  
                        datefmt="%H:%M:%S", filename= log_file_path, filemode= 'w')

version = create_string_buffer(16)
dwf.FDwfGetVersion(version)
print("Version: "+str(version.value))

cdevices = c_int()
dwf.FDwfEnum(0, byref(cdevices))
print("Number of Devices: "+str(cdevices.value))

if cdevices.value == 0:
    print("no device detected")
    quit()

dwf.FDwfParamSet(DwfParamOnClose, 0) # 0 = run, 1 = stop, 2 = shutdown

print("Opening first device")
hdwf = c_int()
dwf.FDwfDeviceOpen(-1, byref(hdwf))

if hdwf.value == hdwfNone.value:
    print("failed to open device")
    quit()

dwf.FDwfDeviceAutoConfigureSet(hdwf, 0) # 0 = the device will only be configured when FDwf###Configure is called

print("Configuring device...")

# wave gen
w1_gate = 0
w2_drain = 1

# Drain: DC
drain_voltage = -0.2 # -5e-3 [V]: limit of the wave generator
dwf.FDwfAnalogOutEnableSet(hdwf, c_int(w2_drain), 1) 
dwf.FDwfAnalogOutFunctionSet(hdwf, c_int(w2_drain), funcDC)
dwf.FDwfAnalogOutOffsetSet(hdwf, c_int(w2_drain), c_double(drain_voltage))
# FDwfAnalogOutConfigure(HDWF hdwf, int idxChannel, int fStart)
# fStart – Start the instrument: 0 stop, 1 start, 3 apply.
dwf.FDwfAnalogOutConfigure(hdwf, c_int(w2_drain), 0)

gate_voltage = 0 # [V]
dwf.FDwfAnalogOutEnableSet(hdwf, c_int(w1_gate), 1) 
dwf.FDwfAnalogOutFunctionSet(hdwf, c_int(w1_gate), funcDC) 
dwf.FDwfAnalogOutOffsetSet(hdwf, c_int(w1_gate), c_double(gate_voltage))
dwf.FDwfAnalogOutConfigure(hdwf, c_int(w1_gate), 0)

# scope:
buffer_size = 100
rec_freq = 50e+3 
# the collecting time: buffer_size/rec_freq
range_set = 5
osc_1_current = 0
osc_2_volt = 1
# FDwfAnalogInChannelEnableSet(HDWF hdwf, int idxChannel, int fEnable)
# fEnable – Set TRUE to enable, FALSE to disable (default)
dwf.FDwfAnalogInChannelEnableSet(hdwf, c_int(osc_1_current), 1)
dwf.FDwfAnalogInChannelEnableSet(hdwf, c_int(osc_2_volt), 1)
dwf.FDwfAnalogInFrequencySet(hdwf, c_double(rec_freq))
dwf.FDwfAnalogInChannelRangeSet(hdwf, c_int(osc_1_current), c_double(range_set))
dwf.FDwfAnalogInChannelRangeSet(hdwf, c_int(osc_2_volt), c_double(range_set))
# FDwfAnalogInBufferSizeSet(HDWF hdwf, int nSize)
dwf.FDwfAnalogInBufferSizeSet(hdwf, c_int(buffer_size))
trgsrc = dwfconstants.trigsrcNone
dwf.FDwfAnalogInTriggerSourceSet(hdwf, trgsrc) 
# by default, ACQMODE: acqmodeSingle 
# FDwfAnalogInConfigure(HDWF hdwf, int fReconfigure, int fStart)
dwf.FDwfAnalogInConfigure(hdwf, 1, 0)

print("Wait for the offset to stabilize...")
time.sleep(1)

# prepare the sweep voltage
file_path = "C:/Users/20245580/LabCode/Codes_For_Experiments/exp_data/20250617/transfer_curve.csv"
        # Prepare record file
field_names = ['time', 'i_channel', 'v_gate', 'i_gate']
with open(file_path, 'w') as file:
    file_writer = csv.DictWriter(file, fieldnames=field_names)
    file_writer.writeheader()


# Resistor for current measurement (res)
R = 1 #0.00205806419e+3 # Ohm
settle_time = 0.5 # [s]
rest_duration = 0.5 # [s]
number_of_measurements = 1
gate_voltage_smallest = -0.5
gate_voltage_largest = 0.5
gate_voltage_step = 0.1
voltage_list_forward = np.arange(gate_voltage_smallest, gate_voltage_largest, gate_voltage_step).tolist()
voltage_list_backward = np.arange(gate_voltage_largest, gate_voltage_smallest, -gate_voltage_step).tolist()


logging.info(f"starting the measurement process")
    # start the instrument
        # wavegen
dwf.FDwfAnalogOutConfigure(hdwf, c_int(w1_gate), 1)
dwf.FDwfAnalogOutConfigure(hdwf, c_int(w2_drain), 1)
time.sleep(settle_time)
    # start the measurement reference time
start_time = time.time()
            # start measurement
for i in range(0, number_of_measurements):
    # forward 
    for idx, v in enumerate(voltage_list_forward):                     
                # set the voltage (gate)
        gate_voltage = v
        logging.info(f"set gate voltage {gate_voltage=}")
        dwf.FDwfAnalogOutOffsetSet(hdwf, c_int(w1_gate), c_double(gate_voltage))
            # apply the reconfigure to wavegen
        dwf.FDwfAnalogOutConfigure(hdwf, c_int(w1_gate), c_int(3))
        time.sleep(settle_time)

            # turn on both osc channels
            # FDwfAnalogInConfigure(HDWF hdwf, int fReconfigure, int fStart)
        dwf.FDwfAnalogInConfigure(hdwf, 0, 1)
            # collect data with osc
        sts = c_int()
        while True:
                # FDwfAnalogInStatus(HDWF hdwf, int fReadData, DwfState *psts)
                # fReadData – TRUE if data should be read.
                dwf.FDwfAnalogInStatus(hdwf, 1, byref(sts))
                if sts.value == DwfStateDone.value :
                    break
                time.sleep(0.001)
        print(f"done with {gate_voltage=}")

        rgc1_current = (c_double*buffer_size)()
        rgc2_volt = (c_double*buffer_size)()
        dwf.FDwfAnalogInStatusData(hdwf, osc_1_current, rgc1_current, len(rgc1_current)) # get channel 1 data
        dwf.FDwfAnalogInStatusData(hdwf, osc_2_volt, rgc2_volt, len(rgc2_volt)) # get channel 2 data

        rgc1_current = list(rgc1_current)
        rgc2_volt = list(rgc2_volt)

        rgc1_current_avg = (sum(rgc1_current) / len(rgc1_current)) / R
        rgc2_volt_avg = sum(rgc2_volt) / len(rgc2_volt)

                # record to file
        with open(file_path, 'a') as file: 
                # NOTICE: THE WHILE LOOP/ FOR LOOP INSIDE -> NO CONSTANT UPDATE TO FILE AT ALL -> NO ANIMATION
            file_writer = csv.DictWriter(file, fieldnames=field_names)
        
            info = {
                        'time': time.time() - start_time,
                        'i_channel': rgc1_current_avg,
                        'v_gate': rgc2_volt_avg,
                        'i_gate': rgc1_current_avg
                                        }
            logging.info(f"save {info=} to .csv")
            file_writer.writerow(info)
                                
            # Rest between measurement
        time.sleep(rest_duration)
        
        
        # backward
    for idx, v in enumerate(voltage_list_backward):     
        # set the voltage (gate)
        gate_voltage = v
        logging.info(f"set gate voltage {gate_voltage=}")
        dwf.FDwfAnalogOutOffsetSet(hdwf, c_int(w1_gate), c_double(gate_voltage))
            # apply the reconfigure to wavegen
        dwf.FDwfAnalogOutConfigure(hdwf, c_int(w1_gate), c_int(3))
        time.sleep(settle_time)

            # turn on both osc channels
            # FDwfAnalogInConfigure(HDWF hdwf, int fReconfigure, int fStart)
        dwf.FDwfAnalogInConfigure(hdwf, 0, 1)
            # collect data with osc
        sts = c_int()
        while True:
                # FDwfAnalogInStatus(HDWF hdwf, int fReadData, DwfState *psts)
                # fReadData – TRUE if data should be read.
                dwf.FDwfAnalogInStatus(hdwf, 1, byref(sts))
                if sts.value == DwfStateDone.value :
                    break
                time.sleep(0.001)
        print(f"done with {gate_voltage=}")

        rgc1_current = (c_double*buffer_size)()
        rgc2_volt = (c_double*buffer_size)()
        dwf.FDwfAnalogInStatusData(hdwf, osc_1_current, rgc1_current, len(rgc1_current)) # get channel 1 data
        dwf.FDwfAnalogInStatusData(hdwf, osc_2_volt, rgc2_volt, len(rgc2_volt)) # get channel 2 data

        rgc1_current = list(rgc1_current)
        rgc2_volt = list(rgc2_volt)

        rgc1_current_avg = (sum(rgc1_current) / len(rgc1_current)) / R
        rgc2_volt_avg = sum(rgc2_volt) / len(rgc2_volt)

                # record to file
        with open(file_path, 'a') as file: 
                # NOTICE: THE WHILE LOOP/ FOR LOOP INSIDE -> NO CONSTANT UPDATE TO FILE AT ALL -> NO ANIMATION
            file_writer = csv.DictWriter(file, fieldnames=field_names)
        
            info = {
                        'time': time.time() - start_time,
                        'i_channel': rgc1_current_avg,
                        'v_gate': rgc2_volt_avg,
                        'i_gate': rgc1_current_avg
                                        }
            logging.info(f"save {info=} to .csv")
            file_writer.writerow(info)
                                
            # Rest between measurement
        time.sleep(rest_duration)
        
print(f"All Done")
dwf.FDwfDeviceCloseAll()

