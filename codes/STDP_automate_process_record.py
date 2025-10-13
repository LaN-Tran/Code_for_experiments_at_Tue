"""
    Automation Keithley 2602B, AD3
    Keithley pulse drain (smua), pulse gate (smub)
    Author:  Tran Le Phuong Lan.
    Created:  2025-09-05

    Requires:                       
       Python 2.7, 3
       pyvisa
       pyusb
       Keithley2600
    Reference:
        [1] https://github.com/LaN-Tran/Automate_Lab_Instrument/tree/main/20250905

"""

import pyvisa
import time
import logging
import pyfirmata
import csv
import os
import sys
from datetime import datetime


    # # ======
    # # Logger
    # # ======
# init logger
format = "%(asctime)s: %(message)s"
log_file_path = 'example.log'
logging.basicConfig(format=format, level=logging.INFO,  
                        datefmt="%H:%M:%S", filename= log_file_path, filemode= 'w')

        # # ======
        # # Arduino board, change between read and write
        # # ======
logging.info("configure arduino mux")
    # MUX 1 (Y0: transfer curve, Y1: ecram)
# arduino_bin_mux1_z =  3# 

arduino_bin_mux1_s0 = 5 # (lsb)
arduino_bin_mux1_s1 = 7 #
arduino_bin_mux1_s2 = 9 # (msb)

arduino_bin_mux1_enable = 11 #

    # MUX 2 (Y0: transfer curve, Y1: ecram)
# arduino_bin_mux2_z = 2 # (HIGH = OFF/ LOW = ON)

arduino_bin_mux2_s0 = 4 # (lsb)
arduino_bin_mux2_s1 = 6 #
arduino_bin_mux2_s2 = 8 # (msb)

arduino_bin_mux2_enable = 10 #
    # init arduino aboard
arduino_board = pyfirmata.Arduino('COM4')
arduino_board.digital[arduino_bin_mux1_enable].write(1)
arduino_board.digital[arduino_bin_mux2_enable].write(1)

        # ======
        # Keithley, smua drain for read
        # ======
rm = pyvisa.ResourceManager('C:/windows/System32/visa64.dll')
logging.info("OPEN keithley resource for reading")


        # ======
        # Upload the keithley scripts to keithley for the program
        # ======

# script for reading phase
file_tsp_path = "C:\\Users\\20245580\\work\\Code_for_experiments_at_Tue\\codes\\single_pulse_measurement_automate_stdp.tsp"
logging.info("UPLOAD read keithley ")
# keithley_instrument.write(f"loadscript Read")
# with open(file_tsp_path) as fp:
#     for line in fp: keithley_instrument.write(line)
# keithley_instrument.write("endscript") 

        # # ======
        # # record to file
        # # ======
file_path = "C:\\Users\\20245580\\work\\Code_for_experiments_at_Tue\\exp_data/20251013/stdp_process_monitor_exp.csv"
file_path_processed_stdp= "C:\\Users\\20245580\\work\\Code_for_experiments_at_Tue\\exp_data/20251013/stdp_processed.csv"
                # ======
                # Prepare record file
                # ======
logging.info("Prepare record file")
field_names = ['time', 'i_channel', 'date_time', 'comment']
if os.path.exists(file_path):
        print("File exists.")
else:
        print("File \\stdp_process_monitor_exp.csv\\ not exist. create file")
        with open(file_path, 'a') as file:
                file_writer = csv.DictWriter(file, fieldnames=field_names)
                file_writer.writeheader()

field_names_processed = ['delta', 'change_percentage']
if os.path.exists(file_path_processed_stdp):
        print("File exists.")
else:
        print("File \\stdp_processed.csv\\ not exist. create file")
        with open(file_path_processed_stdp, 'a') as file:
                file_writer = csv.DictWriter(file, fieldnames=field_names_processed)
                file_writer.writeheader()

        # ======
        # Measurement parameters
        # ======
pulse_width_read = 0.02 # [s]
read_pulse_off = 1.5 # [s]
number_read_pulses = 1
pulse_period_read = pulse_width_read +  read_pulse_off # [s]
read_func_complete = (pulse_period_read)*number_read_pulses

arduino_settle_time = 1 # [s]
wait_between_exp = 1 # [s]
# for g_init
num_rps = 3
# for g_after
num_rps_after_stdp = 5

        # ======
        # start measurement
        # ======
logging.info("start measurement")
time_ref = time.time()

logging.info("comment about the exp")
comment_exp = input("(dg or gd), NO SPACE: ")

try:
    
        logging.info("CONFIGURE transfer curve setup")
        # # arduino mux1 connect to Y0
                # Y0 configure
        arduino_board.digital[arduino_bin_mux1_s0].write(0)
        arduino_board.digital[arduino_bin_mux1_s1].write(0)
        arduino_board.digital[arduino_bin_mux1_s2].write(0)
                # close switch
        arduino_board.digital[arduino_bin_mux1_enable].write(0)
        time.sleep(arduino_settle_time)

        # # arduino mux2 connect to Y0
                # Y0 configure
        arduino_board.digital[arduino_bin_mux2_s0].write(0)
        arduino_board.digital[arduino_bin_mux2_s1].write(0)
        arduino_board.digital[arduino_bin_mux2_s2].write(0)
                # close switch
        arduino_board.digital[arduino_bin_mux2_enable].write(0)
        time.sleep(arduino_settle_time)
        logging.info("FINISH transfer curve setup")
        
        logging.info("RUN transfer curve")
        import keithley_transfer_curve_automate_stdp
                #         # open switch
        arduino_board.digital[arduino_bin_mux1_enable].write(1)
        arduino_board.digital[arduino_bin_mux2_enable].write(1)
        logging.info("FINISH RUN transfer curve")

        logging.info("CONFIGURE ECRAM setup")
        # # arduino mux1 connect to Y1
                # Y1 configure
        arduino_board.digital[arduino_bin_mux1_s0].write(0)
        arduino_board.digital[arduino_bin_mux1_s1].write(1)
        arduino_board.digital[arduino_bin_mux1_s2].write(0)
                # close switch
        arduino_board.digital[arduino_bin_mux1_enable].write(0)
        time.sleep(arduino_settle_time)

        # # arduino mux2 connect to Y1
                # Y1 configure
        arduino_board.digital[arduino_bin_mux2_s0].write(0)
        arduino_board.digital[arduino_bin_mux2_s1].write(1)
        arduino_board.digital[arduino_bin_mux2_s2].write(0)
                # close switch
        arduino_board.digital[arduino_bin_mux2_enable].write(0)
        time.sleep(arduino_settle_time)
        logging.info("FINISH ECRAM setup")


        logging.info("STDP MEASUREMENT Start")

        # REFERENCE TIME
        time_ref = time.time()
                        # read
        logging.info("reading initial channel conductance")
        record_g_init = []

        logging.info("OPEN keithley resource for reading")
        keithley_instrument = rm.open_resource('TCPIP0::169.254.0.1::inst0::INSTR')
        keithley_instrument.timeout = 20000
        logging.info("UPLOAD read keithley ")
        keithley_instrument.write(f"loadscript Read")
        with open(file_tsp_path) as fp:
                for line in fp: keithley_instrument.write(line)
        keithley_instrument.write("endscript") 

        for idx_exp in range(0, num_rps):
                
                # read
                logging.info("reading phase")
                print("read phase")
                try:
                        keithley_instrument.write("Read.run()")

                        time.sleep(read_func_complete)

                        logging.info(f"read successfully")
                        # save to file
                        cur_time = time.time()
                        cur_datetime = datetime.now()
                        n_samples = int(float(keithley_instrument.query(f"print(smua.nvbuffer1.n)")))
                        average = 0
                        for i in range(0, n_samples):
                                measured_i = float(keithley_instrument.query(f"print(smua.nvbuffer1.readings[{i}+1])"))
                                keithely_time_stamp = float(keithley_instrument.query(f"print(smua.nvbuffer1.timestamps[{i}+1])"))
                                measured_vd = float(keithley_instrument.query(f"print(smua.nvbuffer1.sourcevalues[{i}+1])"))
                                with open(file_path, 'a') as file: 
                                                # NOTICE: THE WHILE LOOP/ FOR LOOP INSIDE -> NO CONSTANT UPDATE TO FILE AT ALL -> NO ANIMATION
                                        file_writer = csv.DictWriter(file, fieldnames=field_names)
                                        info = {
                                                'time':cur_time - time_ref + keithely_time_stamp,
                                                'i_channel': measured_i,
                                                'date_time': cur_datetime,
                                                'comment': comment_exp
                                                }
                                        file_writer.writerow(info)
                                average = average + measured_i
                        average = average/ n_samples
                        record_g_init.append(average)
                except Exception as e:
                        logging.info(f"Keithley error: {e=}")
                        logging.info(f"EXIT: {e=}")
                                # open switch
                        arduino_board.digital[arduino_bin_mux1_enable].write(1)
                        arduino_board.digital[arduino_bin_mux2_enable].write(1)
                        sys.exit(-1)

                # wait between exp
                time.sleep(wait_between_exp)
        
        logging.info("FINISH initial read, close keithley resource for another code")
        keithley_instrument.close()
        
        logging.info("Set dg/gd (Drain=Pre before Gate=Post)")
        filename = 'C:\\Users\\20245580\\work\\Code_for_experiments_at_Tue\\codes\\keithley_interchannelPulseTrain_stdp_automate.py'
        with open(filename, 'r') as file:
                lines = file.readlines()
        # point to tsp run file
        if comment_exp == 'dg':
                lines[50]= 'file_tsp_path = \"C:/Users/20245580/work/Code_for_experiments_at_Tue/codes/pulse_train_2ch_dg_automate_stdp.tsp\"' \
                                        + '\n'
        if comment_exp == 'gd':
                lines[50]= 'file_tsp_path = \"C:/Users/20245580/work/Code_for_experiments_at_Tue/codes/pulse_train_2ch_gd_automate_stdp.tsp\"' \
                                        + '\n' 
        # Write the modified lines back to the file
        with open(filename, 'w') as file:
                file.writelines(lines)
        
        # record the delta_t
        delta_t = 0.002
        if comment_exp == 'dg':
                delta_t = -delta_t

        logging.info("RUN dg/gd (Drain=Pre before Gate=Post)")
        import keithley_interchannelPulseTrain_stdp_automate
        logging.info("FINISH dg/gd (Drain=Pre before Gate=Post)")
        
        logging.info("READING channel conductance, after stdp")

        logging.info("OPEN keithley resource for reading")
        keithley_instrument = rm.open_resource('TCPIP0::169.254.0.1::inst0::INSTR')
        keithley_instrument.timeout = 10000
        logging.info("UPLOAD read keithley ")
        keithley_instrument.write(f"loadscript Read")
        with open(file_tsp_path) as fp:
                for line in fp: keithley_instrument.write(line)
        keithley_instrument.write("endscript") 

        logging.info("READING... ")
        record_g_after = []
        for idx_exp in range(0, num_rps_after_stdp):
                
                # read
                logging.info("reading phase")
                print("read phase")
                try:
                        keithley_instrument.write("Read.run()")

                        time.sleep(read_func_complete)

                        logging.info(f"read successfully")
                        # save to file
                        cur_time = time.time()
                        cur_datetime = datetime.now()
                        n_samples = int(float(keithley_instrument.query(f"print(smua.nvbuffer1.n)")))
                        average = 0
                        for i in range(0, n_samples):
                                measured_i = float(keithley_instrument.query(f"print(smua.nvbuffer1.readings[{i}+1])"))
                                keithely_time_stamp = float(keithley_instrument.query(f"print(smua.nvbuffer1.timestamps[{i}+1])"))
                                measured_vd = float(keithley_instrument.query(f"print(smua.nvbuffer1.sourcevalues[{i}+1])"))
                                with open(file_path, 'a') as file: 
                                                # NOTICE: THE WHILE LOOP/ FOR LOOP INSIDE -> NO CONSTANT UPDATE TO FILE AT ALL -> NO ANIMATION
                                        file_writer = csv.DictWriter(file, fieldnames=field_names)
                                        info = {
                                                'time':cur_time - time_ref + keithely_time_stamp,
                                                'i_channel': measured_i,
                                                'date_time': cur_datetime,
                                                'comment': comment_exp 
                                                }
                                        file_writer.writerow(info)
                                average = average + measured_i
                        average = average/ n_samples
                        record_g_after.append(average)
                except Exception as e:
                        logging.info(f"Keithley error: {e=}")
                        logging.info(f"EXIT: {e=}")
                        sys.exit(-1)

                # wait between exp
                time.sleep(wait_between_exp)

        keithley_instrument.close()
        logging.info("MEASUREMENT FINISH")
        
        logging.info("POST STDP PROCESSING")
        g_init_avg = sum(record_g_init)/len(record_g_init)
        g_after_avg = sum(record_g_after)/len(record_g_after)
        percentage_change =  (g_after_avg - g_init_avg)/ g_init_avg
        with open(file_path_processed_stdp, 'a') as file: 
                # NOTICE: THE WHILE LOOP/ FOR LOOP INSIDE -> NO CONSTANT UPDATE TO FILE AT ALL -> NO ANIMATION
                file_writer = csv.DictWriter(file, fieldnames=field_names_processed)
                info = {
                                                'delta': delta_t,
                                                'change_percentage': percentage_change
                                                }
                file_writer.writerow(info)

except KeyboardInterrupt:
    print(f"MEASUREMENT: EXIT KeyboardInterrupt")
    keithley_instrument.write(f"smua.source.output = smua.OUTPUT_OFF")
    keithley_instrument.write(f"smub.source.output = smub.OUTPUT_OFF")
    rm.close()

