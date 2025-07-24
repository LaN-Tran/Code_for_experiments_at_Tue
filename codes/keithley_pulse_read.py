"""
    Automation Keithley 2602B measurement
    Keithley pulse, measure
    Author:  Tran Le Phuong Lan.
    Created:  2025-07-24

    Requires:                       
       Python 2.7, 3
       pyvisa
       pyusb
    Reference:

"""

import pyvisa
from  keithley2600 import Keithley2600

        # ======
        # Keithley
        # ======
k = Keithley2600('USB0::0x05E6::0x2636::4480001::INSTR', visa_library = 'C:/windows/System32/visa64.dll', timeout = 100000)
k.timeout = 
k.smua.source.output = k.smua.OUTPUT_OFF
