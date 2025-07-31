"""
    Automation Keithley 2602B measurement
    Keithley pulse, measure
    Author:  Tran Le Phuong Lan.
    Created:  2025-07-29

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
from datetime import datetime
import csv
import sys

import os


        # # ======
        # # record to file
        # # ======
file_path = "C:/Users/20245580/LabCode/Codes_For_Experiments/exp_data/20250731/pulse_exp_prototype_1v2.csv"
file_path_avg = "C:/Users/20245580/LabCode/Codes_For_Experiments/exp_data/20250731/pulse_exp_avg_prototype_1v2.csv"
                # ======
                # Prepare record file
                # ======
field_names = ['time', 'i_channel', 'v_drain', 'date_time', 'preced_gate_pulse']
if os.path.exists(file_path):
        print("File exists.")
else:
        print("File not exist. create file")
        with open(file_path, 'a') as file:
                file_writer = csv.DictWriter(file, fieldnames=field_names)
                file_writer.writeheader()

field_names_avg = ['time', 'i_channel_avg', 'date_time', 'preced_gate_pulse']
if os.path.exists(file_path_avg):
        print("File exists.")
else:
        print("File not exist. create file")
        with open(file_path_avg, 'a') as file:
                file_writer = csv.DictWriter(file, fieldnames=field_names_avg)
                file_writer.writeheader()

        # ======
        # Keithley
        # ======
k = Keithley2600('USB0::0x05E6::0x2602::4522205::INSTR', visa_library = 'C:/windows/System32/visa64.dll', timeout = 100000)
k.smua.source.output = k.smua.OUTPUT_OFF
k.smub.source.output = k.smub.OUTPUT_OFF

# SMUA (drain parameters)
pulse_volt = 0.8 # [V]
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

        # configure smub (gate)
gate_volt = 0.0
#-- Restore 2600B defaults.
k.smub.reset()
#-- source voltage so set the range for voltage source
k.smub.source.rangev = gate_volt # [V]
#-- bias
k.smub.source.levelv =  gate_volt # [V] 
#-- set source function
k.smub.source.func = k.smub.OUTPUT_DCVOLTS

        # ======
        # start measurement
        # ======
print("start measurement")
time_ref = time.time()

try:
        # input about the record
        preceeded_gate_pulse = input("Preceded by gate pulse: ")

        # start the gate voltage
        k.smub.source.output = k.smub.OUTPUT_ON
        # time.sleep(0.5)
        # start the drain pulse voltage
        k.smua.source.output = k.smua.OUTPUT_ON
        number_reading_pulses = 5
        t_on = 100e-3 # [s]
        t_off = 5000e-3 # [s]
        # time.sleep(5)
        k.smua.measure.nplc = 1 # [PLC], PLC = 50Hz = 20ms; nplc < ton 
        try: 
                k.PulseVMeasureI(k.smua, bias_volt, pulse_volt, t_on, t_off, number_reading_pulses)

                #  save to file
                cur_time = time.time()
                cur_datetime = datetime.now()
                print(f"{k.smua.nvbuffer1.n}")
                n_samples = k.smua.nvbuffer1.n

                average = 0
                for i in range(0, n_samples):
                        print(f"{i=} {'='*10}")
                        measured_i = k.smua.nvbuffer1.readings[i+1] 
                        vd = k.smua.nvbuffer1.sourcevalues[i+1]
                        keithely_time_stamp = k.smua.nvbuffer1.timestamps[i+1]
                        # exp_result.append(measured_i)
                        average = average + measured_i
                        print(f"{measured_i=} @ {gate_volt=}")
                        print(f"{vd=}")
                        print(f"{keithely_time_stamp=}")
                        with open(file_path, 'a') as file: 
                                        # NOTICE: THE WHILE LOOP/ FOR LOOP INSIDE -> NO CONSTANT UPDATE TO FILE AT ALL -> NO ANIMATION
                                file_writer = csv.DictWriter(file, fieldnames=field_names)
                                info = {
                                        'time':cur_time - time_ref+ keithely_time_stamp,
                                        'i_channel': measured_i,
                                        'v_drain' : vd,
                                        'date_time': cur_datetime,
                                        'preced_gate_pulse': preceeded_gate_pulse
                                        }
                                file_writer.writerow(info)

                average = average/ n_samples
                with open(file_path_avg, 'a') as file: 
                        # NOTICE: THE WHILE LOOP/ FOR LOOP INSIDE -> NO CONSTANT UPDATE TO FILE AT ALL -> NO ANIMATION
                        file_writer = csv.DictWriter(file, fieldnames=field_names_avg)
                        info = {
                        'time':cur_time - time_ref,
                        'i_channel_avg': average,
                        'date_time': cur_datetime,
                        'preced_gate_pulse': preceeded_gate_pulse
                                }
                        file_writer.writerow(info)
        except Exception as e:
                print(f"Error: {e=}")  
                sys.exit(-1)
                k.smua.source.output = k.smua.OUTPUT_OFF
                k.smub.source.output = k.smub.OUTPUT_OFF

        # avg_exp_result.append(average)
        print(f"MEASUREMENT: DONE")
        k.smua.source.output = k.smua.OUTPUT_OFF
        k.smub.source.output = k.smub.OUTPUT_OFF

    
except KeyboardInterrupt:
    print(f"MEASUREMENT: EXIT, ERROR")
    k.smua.source.output = k.smua.OUTPUT_OFF
    k.smub.source.output = k.smub.OUTPUT_OFF
