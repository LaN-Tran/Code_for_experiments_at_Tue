"""
    Rigol Ds1054
    Trigger on CH2, collect from CH1
    Author:  Tran Le Phuong Lan.
    Created:  2025-07-24

    Requires:                       
       Python 2.7, 3
       pyvisa
       pyusb
    Reference:
"""

import pyvisa
import time
import csv
import logging
import numpy as np

    # # ======
    # # Logger
    # # ======
# init logger
format = "%(asctime)s: %(message)s"
log_file_path = 'example.log'
logging.basicConfig(format=format, level=logging.INFO,  
                        datefmt="%H:%M:%S", filename= log_file_path, filemode= 'w')

    # # ======
    # # Connect and prepare the Rigol osc
    # # ======
rm = pyvisa.ResourceManager('C:/windows/System32/visa64.dll')
osc_rig = rm.open_resource('USB0::0x1AB1::0x04CE::DS1ZA221403528::INSTR')
osc_rig.timeout = 1500 # [ms]

    # # ======
    # # Record file
    # # ======
        # path to the measurement record
file_path = "C:/Users/20245580/LabCode/Codes_For_Experiments/exp_data/20250724/"
field_names = ['time', 'volts']


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
samples_in_a_batch = 200000

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

n_exp = 5

try:
    for idx_exp in range(0, n_exp):
            # OSC
            # check whether there is data to collect and save it to file
        while True:
            trigger_sts = osc_rig.query(':TRIG:STAT?')
            logging.info(f"osc: {trigger_sts=}")
            if 'STOP' in trigger_sts:
                break    

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
        file_path_trace = file_path + 'trace_after_5dp_' + str(idx_exp) +'.csv'
                    
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
                # osc_rig.write(':RUN')
            osc_rig.write(':SING')
except KeyboardInterrupt:
    logging.info(f"OSC: EXIT")
    osc_rig.write(':STOP')
