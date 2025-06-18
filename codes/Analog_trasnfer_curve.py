"""
   DWF Python Example
   Author:  Digilent, Inc.
   Modifier: Tran Le Phuong Lan
   Revision:  2025-06-17

   Requires:                       
       Python 2.7, 3
   NPN transistor test
   Physical setup: https://digilent.com/reference/test-and-measurement/guides/waveforms-curve-tracer?srsltid=AfmBOoqN0yxSmK0MYBprgry4HaLvbSzvA-zQUWobe24-F8WjA6Xg2Gkq
"""

from ctypes import *
import time
import sys
from os import sep
import matplotlib.pyplot as plt
import numpy

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
# Drain: DC
dwf.FDwfAnalogOutEnableSet(hdwf, 1, 1) 
dwf.FDwfAnalogOutFunctionSet(hdwf, 1, funcDC)
dwf.FDwfAnalogOutOffsetSet(hdwf, 1, c_double(-0.2))
dwf.FDwfAnalogOutConfigure(hdwf, 1, 0)

# Gate: -0.5V to 0.5V (in 5 steps) then 0.5 V back to -0.5V (in 5 steps), at 5Hz, 200ms total length
dwf.FDwfAnalogOutEnableSet(hdwf, 0, 1) 
dwf.FDwfAnalogOutFunctionSet(hdwf, 0, funcCustom) 
dwf.FDwfAnalogOutFrequencySet(hdwf, 0, c_double(5))
dwf.FDwfAnalogOutOffsetSet(hdwf, 0, c_double(0))
dwf.FDwfAnalogOutAmplitudeSet(hdwf, 0, c_double(0.5))
# values normalized to +-1 
# ChatGPT: using Python's ctypes module to create a C-style array of 5 double values.
rgSteps = (c_double*10)(-1.0, -0.6, -0.2, 0.2, 0.6, 1, 0.6, 0.2, -0.2, -0.6) 
# The output value will be Offset + Sample*Amplitude
# The Sample = values in rgSteps
dwf.FDwfAnalogOutDataSet(hdwf, 0, rgSteps, len(rgSteps))
dwf.FDwfAnalogOutRunSet(hdwf, 0, c_double(0.2))
dwf.FDwfAnalogOutRepeatSet(hdwf, 0, 2)
dwf.FDwfAnalogOutMasterSet(hdwf, 0, 1)
dwf.FDwfAnalogOutConfigure(hdwf, 0, 0)

# scope: (50kHz*200ms x 2) samples at 50kHz, 200ms x 2
dwf.FDwfAnalogInChannelEnableSet(hdwf, 0, 1)
dwf.FDwfAnalogInChannelEnableSet(hdwf, 1, 1)
dwf.FDwfAnalogInFrequencySet(hdwf, c_double(50e3))
dwf.FDwfAnalogInChannelRangeSet(hdwf, 0, c_double(10.0))
dwf.FDwfAnalogInChannelRangeSet(hdwf, 1, c_double(10.0))
dwf.FDwfAnalogInBufferSizeSet(hdwf, 20000)
dwf.FDwfAnalogInTriggerSourceSet(hdwf, trigsrcAnalogOut1) 
dwf.FDwfAnalogInTriggerPositionSet(hdwf, c_double(0.01)) # 5ms, trigger at first sample
dwf.FDwfAnalogInConfigure(hdwf, 1, 0)

print("Wait for the offset to stabilize...")
time.sleep(1)

print("Starting test...")
dwf.FDwfAnalogInConfigure(hdwf, 0, 1)
dwf.FDwfAnalogOutConfigure(hdwf, 1, 1)

sts = c_int()
while True:
    dwf.FDwfAnalogInStatus(hdwf, 1, byref(sts))
    if sts.value == DwfStateDone.value :
        break
    time.sleep(0.001)
print("done")

rgc1 = (c_double*20000)()
rgc2 = (c_double*20000)()
dwf.FDwfAnalogInStatusData(hdwf, 0, rgc1, len(rgc1)) # get channel 1 data
dwf.FDwfAnalogInStatusData(hdwf, 1, rgc2, len(rgc2)) # get channel 2 data

dwf.FDwfDeviceCloseAll()

plt.plot(numpy.fromiter(rgc2, dtype = numpy.float), numpy.fromiter(rgc1, dtype = numpy.float))
plt.show()

