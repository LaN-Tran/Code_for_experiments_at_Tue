"""
    Automation Keithley 2602B, AD3
    Keithley pulse drain, measure; AD3 pulse gate write
    Author:  Tran Le Phuong Lan.
    Created:  2025-07-30

    Requires:                       
       Python 2.7, 3
       pyvisa
       pyusb
       Keithley2600
    Reference:

"""

import pyvisa
from  keithley2600 import Keithley2600
import time
import logging

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

        # ======
        # Keithley
        # ======
k = Keithley2600('USB0::0x05E6::0x2602::4522205::INSTR', visa_library = 'C:/windows/System32/visa64.dll', timeout = 100000)
k.smua.source.output = k.smua.OUTPUT_OFF

# SMUA (drain parameters)
pulse_volt = 0.2 # [V]
bias_volt = 0 # [V], positve zero; if pulse negative, set to negative zero

        # configure smua pulse v read I (drain)
#-- Restore 2600B defaults.
k.smua.reset()
#-- source voltage so set the range for voltage source
k.smua.source.rangev = pulse_volt if pulse_volt > bias_volt else bias_volt # [V]
#-- bias
k.smua.source.levelv =  bias_volt # [V] 
#-- set source function
k.smua.source.func = k.smua.OUTPUT_DCVOLTS
#-- Select measure I autorange.
k.smua.measure.autorangei = k.smua.AUTORANGE_ON # (with very small current -> timeout error)
# k.smua.measure.rangei = 1e-7
# turn autozero off for sweeping or time critical measurements
k.smua.measure.autozero = k.smua.AUTOZERO_OFF
k.smua.measure.filter.enable = k.smua.FILTER_OFF 
#-- Select ASCII data format.
# k.format.data = k.format.ASCII

# -- buffer
#-- Clear buffer 1.
k.smua.nvbuffer1.clear()
#-- Enable append buffer mode.
k.smua.nvbuffer1.appendmode = 1
#-- Enable source value storage.
k.smua.nvbuffer1.collectsourcevalues = 1
#-- Enable source value storage.
k.smua.nvbuffer1.collecttimestamps = 1

        # configure AD3 (gate)
gate_volt = 0.0
#-- Restore 2600B defaults.
k.smub.reset()
#-- source voltage so set the range for voltage source
k.smub.source.rangev = gate_volt # [V]
#-- bias
k.smub.source.levelv =  gate_volt # [V] 
#-- set source function
k.smub.source.func = k.smub.OUTPUT_DCVOLTS

        # # ======
        # # AD3 parameters for write phase
        # # ======
# w1_period = write period -> wait time = 0 [s]
# w2_period = w1_period - delta_tpre_tpost ; w2 must have wait time = delta_tpre_tpost 
delta_tpre_tpost = 10e-3 # [s]
n_write_cycle = 1
            
w2_ch_gate = 1
w2_period = w1_period -  delta_tpre_tpost # [s]
pulse_width_ch_2 = w1_pulse_width # [s]
w2_freq = 1/ w2_period # [Hz]
w2_amplitude = 200e-3 # [V]
w2_offset = 0 # [V]
w2_percentageSymmetry = (pulse_width_ch_2 / w2_period) * 100 # pulse width = 100 ms
secWait_2 =  delta_tpre_tpost # [s]

logging.info("configure w2, gate for writing")
dwf.FDwfAnalogOutNodeEnableSet(hdwf, c_int(w2_ch_gate), dwfconstants.AnalogOutNodeCarrier, c_int(1))
dwf.FDwfAnalogOutNodeFunctionSet(hdwf, c_int(w2_ch_gate), dwfconstants.AnalogOutNodeCarrier, dwfconstants.funcPulse)
dwf.FDwfAnalogOutNodeFrequencySet(hdwf, c_int(w2_ch_gate), dwfconstants.AnalogOutNodeCarrier, c_double(w2_freq))
# FDwfAnalogOutNodeSymmetrySet(HDWF hdwf, int idxChannel, AnalogOutNode node, double percentageSymmetry)
dwf.FDwfAnalogOutNodeSymmetrySet(hdwf, c_int(w2_ch_gate), dwfconstants.AnalogOutNodeCarrier, c_double(w2_percentageSymmetry))
dwf.FDwfAnalogOutOffsetSet(hdwf, w2_ch_gate, c_double(w2_offset))
dwf.FDwfAnalogOutNodeAmplitudeSet(hdwf, c_int(w2_ch_gate), dwfconstants.AnalogOutNodeCarrier, c_double(w2_amplitude))
# FDwfAnalogOutRunSet(HDWF hdwf, int idxChannel, double secRun)
secRun = w2_period
dwf.FDwfAnalogOutRunSet(hdwf, c_int(w2_ch_gate), c_double(secRun))
# FDwfAnalogOutRepeatSet(HDWF hdwf, int idxChannel, int cRepeat);
cRepeat = n_write_cycle
dwf.FDwfAnalogOutRepeatSet(hdwf, c_int(w2_ch_gate), c_int(cRepeat))
idle = dwfconstants.DwfAnalogOutIdleOffset
dwf.FDwfAnalogOutIdleSet(hdwf, c_int(w2_ch_gate), idle)
# FDwfAnalogOutTriggerSourceSet(HDWF hdwf, int idxChannel, TRIGSRC trigsrc)
trgsrc = dwfconstants.trigsrcAnalogOut1
dwf.FDwfAnalogOutTriggerSourceSet(hdwf, c_int(w2_ch_gate), trgsrc)
# FDwfAnalogOutTriggerSlopeSet(HDWF hdwf, int idxChannel, DwfTriggerSlope slope)
slope = dwfconstants.DwfTriggerSlopeRise
dwf.FDwfAnalogOutTriggerSlopeSet(hdwf, c_int(w2_ch_gate), slope)
dwf.FDwfAnalogOutWaitSet(hdwf, c_int(w2_ch_gate), c_double(secWait_2))
# apply the configuration
dwf.FDwfAnalogOutConfigure(hdwf, c_int(w2_ch_gate), c_int(0))
time.sleep(ad3_settle_time)

        # ======
        # start measurement
        # ======
try:
    # start the gate voltage
    k.smub.source.output = k.smub.OUTPUT_ON
    # time.sleep(0.5)
    # start the drain pulse voltage
    k.smua.source.output = k.smua.OUTPUT_ON
    number_reading_pulses = 1
    t_on = 100e-3 # [s]
    t_off = 500e-3 # [s]
    # time.sleep(5)
    k.smua.measure.nplc = 1 # [PLC], PLC = 50Hz = 20ms; nplc < ton 
    k.PulseVMeasureI(k.smua, bias_volt, pulse_volt, t_on, t_off, number_reading_pulses)

    # 
    print(f"{k.smua.nvbuffer1.n}")
    n_samples = k.smua.nvbuffer1.n

    average = 0
    for i in range(0, n_samples):
        print(f"{i=} {'='*10}")
        measured_i = k.smua.nvbuffer1.readings[i+1] 
        print(f"{measured_i=} @ {gate_volt=}")
        # exp_result.append(measured_i)
        average = average + measured_i
        print(f"{k.smua.nvbuffer1.sourcevalues[i+1]=}")
        print(f"{k.smua.nvbuffer1.timestamps[i+1]=}")

    average = average/ n_samples
    # avg_exp_result.append(average)
    print(f"MEASUREMENT: DONE")
    k.smua.source.output = k.smua.OUTPUT_OFF
    k.smub.source.output = k.smub.OUTPUT_OFF
    
except KeyboardInterrupt:
    print(f"MEASUREMENT: EXIT, ERROR")
    k.smua.source.output = k.smua.OUTPUT_OFF
    k.smub.source.output = k.smub.OUTPUT_OFF
