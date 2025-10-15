"""
    Automation Keithley 2602B measurement
    Transfer curve experiment
    Author:  Tran Le Phuong Lan.
    Created:  2025-09-17

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
# from  keithley2600 import Keithley2600, ResultTable
import logging
import time
import numpy as np
import os
import matplotlib.pyplot as plt
import csv
import pandas as pd
import matplotlib.animation as animation

# check the instrument (e.g Keithley 2602B) VISA address
# rm = pyvisa.ResourceManager('C:/windows/System32/visa64.dll')
# print(rm.list_resources())


# init logger
format = "%(asctime)s: %(message)s"
log_file_path = 'example.log'
logging.basicConfig(format=format, level=logging.INFO,  
                        datefmt="%H:%M:%S", filename= log_file_path, filemode= 'a')

        # init the instrument handle
    # k = Keithley2600('USB0::0x05E6::0x2636::4480001::INSTR', visa_library = 'C:/windows/System32/visa64.dll')
rm = pyvisa.ResourceManager('C:/windows/System32/visa64.dll')
# keithley_instrument = rm.open_resource('TCPIP0::169.254.0.1::inst0::INSTR')
keithley_instrument = rm.open_resource('TCPIP0::169.254.0.1::inst0::INSTR')
keithley_instrument.timeout = 20000
        # Turn everything OFF
keithley_instrument.write('smua.source.output = smua.OUTPUT_OFF')
keithley_instrument.write('smub.source.output = smub.OUTPUT_OFF')
time.sleep(1)


        # path to the measurement record
file_path = "C:/Users/20245580/work/Code_for_experiments_at_Tue/exp_data/20251015/transfer_curve.csv"

logging.info("Main    : Prepare measurement")

number_of_measurements = 1

settle_time = 1 # s # after the smu configuration
    
sw_settle_time = 10e-3 # s
rest_duration = 0.2 # s

gate_voltage_smallest = -0.3     # V (for liquid electrolite)
gate_voltage_largest = 0.3 # V (for liquid electrolite)
gate_voltage_step = 0.1 # V
drain_voltage = 0.05 # V
try:
                # ======
                # Prepare record file
                # ======
    field_names =  ['time', 'i_channel', 'v_drain','i_gate', 'v_gate']
    with open(file_path, 'w') as file:
        file_writer = csv.DictWriter(file, fieldnames=field_names)
        file_writer.writeheader()

                # ======
                # Configure smub as voltage source (Gate)
                # ======
                    # reset the channel
    keithley_instrument.write('smub.reset()')

                    #-- output off mode
    keithley_instrument.write(f"smub.source.offmode = smub.OUTPUT_NORMAL")
    keithley_instrument.write(f"smub.source.offfunc = smub.OUTPUT_DCVOLTS")
    keithley_instrument.write(f"smub.source.offlimiti = 100e-3")                
                
                # Clear buffer 1.
    keithley_instrument.write('smub.nvbuffer1.clear()')

                    # Select measure I autorange.
    keithley_instrument.write('smub.measure.autozero = smub.AUTOZERO_OFF') # ? more stable with AUTOZERO_AUTO, 
                                                                                        # when the measured current is ~.e-13
    keithley_instrument.write('smub.measure.autorangei = smub.AUTORANGE_ON')

                    # Select the voltage source function.
    keithley_instrument.write('smub.source.func = smub.OUTPUT_DCVOLTS')
                    
                    # Set the bias voltage.
    keithley_instrument.write(f"smub.source.levelv = {gate_voltage_smallest}")


                    

                # # ======
                # # Configure smua as source v, measure i (Drain)
                # # ======

                    # Restore 2600B defaults.
    keithley_instrument.write('smua.reset()')

                    #-- output off mode
    keithley_instrument.write(f"smua.source.offmode = smua.OUTPUT_NORMAL")
    keithley_instrument.write(f"smua.source.offfunc = smua.OUTPUT_DCVOLTS")
    keithley_instrument.write(f"smua.source.offlimiti = 100e-3")   

                    # Select channel A display.
    keithley_instrument.write(f"display.screen = display.SMUA")

                    # Display current.
    keithley_instrument.write(f"display.smua.measure.func = display.MEASURE_DCAMPS")

                    # Select measure I autorange.
    keithley_instrument.write(f"smua.measure.autozero = smua.AUTOZERO_OFF")
    keithley_instrument.write(f"smua.measure.autorangei = smua.AUTORANGE_ON")

                    # Select ASCII data format.
                # smu.write('format.data = format.ASCII')

                    # Clear buffer 1.
    keithley_instrument.write(f"smua.nvbuffer1.clear()")

                    # Select the source voltage function.
    keithley_instrument.write(f"smua.source.func = smua.OUTPUT_DCVOLTS")

                    # Set the bias voltage.
    keithley_instrument.write(f"smua.source.levelv =  {drain_voltage}")

                # # ======
                # # Measuring
                # # ======

                    # Turn on the gate source.
    keithley_instrument.write(f"smub.source.output = smub.OUTPUT_ON")

                    # Turn on the drain source.
    keithley_instrument.write(f"smua.source.output = smua.OUTPUT_ON")

                    # Settling time
    time.sleep(settle_time)

                    # prepare the sweep voltage
    voltage_list_forward = np.arange(gate_voltage_smallest, gate_voltage_largest, gate_voltage_step).tolist()
    voltage_list_backward = np.arange(gate_voltage_largest, gate_voltage_smallest, -gate_voltage_step).tolist()
    logging.info(f"starting the measurement process")
                    # start the measurement reference time
    start_time = time.time()
                    # start measurement
    for i in range(0, number_of_measurements):
        # forward 
        for idx, v in enumerate(voltage_list_forward):     
            with open(file_path, 'a') as file: 
                        # NOTICE: THE WHILE LOOP/ FOR LOOP INSIDE -> NO CONSTANT UPDATE TO FILE AT ALL -> NO ANIMATION
                file_writer = csv.DictWriter(file, fieldnames=field_names)
                            
                                # set the voltage (gate)
                logging.info(f"set gate voltage {v=}")
                keithley_instrument.write(f"smub.source.levelv = {v}")
                time.sleep(settle_time)
                try:
                    measured_i_channel = float(keithley_instrument.query('print(smua.measure.i())'))
                    measured_v_drain = float(keithley_instrument.query('print(smua.measure.v())'))
                    measured_i_gate =  float(keithley_instrument.query('print(smub.measure.i())'))
                    measured_v_gate = float(keithley_instrument.query('print(smub.measure.v())'))

                                # measured_i_gate = keithley_instrument.smub.measure.i()

                                    # record to file
                    info = {
                        'time': time.time() - start_time,
                        'i_channel': measured_i_channel,
                        'v_drain': measured_v_drain,
                        'i_gate': measured_i_gate,
                        'v_gate': measured_v_gate,
                                                    }
                    logging.info(f"save {info=} to .csv")
                    file_writer.writerow(info)

                except Exception as e:
                                # # ======
                                # # Open all switches
                                # # ======
                                # For the relay board: HIGH = OFF = OPEN // LOW = ON = CLOSE
                    keithley_instrument.write(f"smua.source.output = smua.OUTPUT_OFF")
                    keithley_instrument.write(f"smub.source.output = smub.OUTPUT_OFF")
                    keithley_instrument.close()
                    logging.info(f"ERROR: keithley measurement: {e=}")
                    

                                    
                                # Rest between measurement
        time.sleep(rest_duration)
            
        
            # wait for the open transition to tbe stable
        time.sleep(0.5)

                    # # ======
                    # # Measuring
                    # # ======

                        # Turn on the gate source.
        keithley_instrument.write(f"smub.source.output = smub.OUTPUT_ON")


                        # Turn on the drain source.
        keithley_instrument.write(f"smua.source.output = smua.OUTPUT_ON")


                        # Settling time
        time.sleep(settle_time)

            # backward
        for idx, v in enumerate(voltage_list_backward):     
            with open(file_path, 'a') as file: 
                        # NOTICE: THE WHILE LOOP/ FOR LOOP INSIDE -> NO CONSTANT UPDATE TO FILE AT ALL -> NO ANIMATION
                file_writer = csv.DictWriter(file, fieldnames=field_names)
                            
                                # set the voltage (gate)
                logging.info(f"set gate voltage {v=}")
                keithley_instrument.write(f"smub.source.levelv = {v}")
                time.sleep(settle_time)
                try:
                    measured_i_channel = float(keithley_instrument.query('print(smua.measure.i())'))
                    measured_v_drain = float(keithley_instrument.query('print(smua.measure.v())'))
                    measured_i_gate =  float(keithley_instrument.query('print(smub.measure.i())'))
                    measured_v_gate = float(keithley_instrument.query('print(smub.measure.v())'))

                                # measured_i_gate = keithley_instrument.smub.measure.i()

                                    # record to file
                    info = {
                        'time': time.time() - start_time,
                        'i_channel': measured_i_channel,
                        'v_drain': measured_v_drain,
                        'i_gate': measured_i_gate,
                        'v_gate': measured_v_gate,
                                                    }
                    logging.info(f"save {info=} to .csv")
                    file_writer.writerow(info)

                except Exception as e:
                                # # ======
                                # # Open all switches
                                # # ======
                                # For the relay board: HIGH = OFF = OPEN // LOW = ON = CLOSE
                
                    keithley_instrument.write(f"smua.source.output = smua.OUTPUT_OFF")
                    keithley_instrument.write(f"smub.source.output = smub.OUTPUT_OFF")
                    keithley_instrument.close()
                    logging.info(f"ERROR: keithley measurement {e=}")

                                # Rest between measurement
        time.sleep(rest_duration)
        
        # # ======
        # # Open all switches
        # # ======
    logging.info("Keithley measurement    : EXIT NORMALLY")
            # turn off the keithley
    keithley_instrument.write(f"smua.source.levelv =  0")
    keithley_instrument.write(f"smub.source.levelv =  0")
    time.sleep(5)
    
    keithley_instrument.write(f"smua.source.output = smua.OUTPUT_OFF")
    keithley_instrument.write(f"smub.source.output = smub.OUTPUT_OFF")
    keithley_instrument.close()
    time.sleep(5)
    # keithley_instrument.write(f"smua.source.output = smua.OUTPUT_OFF")
    # keithley_instrument.write(f"smub.source.output = smub.OUTPUT_OFF")

except KeyboardInterrupt:
     # # ======
        # # Open all switches
        # # ======
    logging.info("Keithley measurement    : EXIT INTERRUPTED")
            # turn off the keithley
    keithley_instrument.write(f"smua.source.levelv =  0")
    keithley_instrument.write(f"smub.source.levelv =  0")
    time.sleep(5)

    keithley_instrument.write(f"smua.source.output = smua.OUTPUT_OFF")
    keithley_instrument.write(f"smub.source.output = smub.OUTPUT_OFF")
    keithley_instrument.close()
    time.sleep(5)




