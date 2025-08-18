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
import pyfirmata
import csv
import os
from datetime import datetime

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
        # Keithley, smua drain for read
        # ======
keithley_instrument = Keithley2600('USB0::0x05E6::0x2636::4480001::INSTR', visa_library = 'C:/windows/System32/visa64.dll', timeout = 100000)
keithley_instrument.smua.source.output = keithley_instrument.smua.OUTPUT_OFF

# SMUA (drain parameters)
pulse_volt = 0.4 # [V]
bias_volt = 0 # [V], positve zero; if pulse negative, set to negative zero

        # configure smua pulse v read I (drain)
#-- Restore 2600B defaults.
keithley_instrument.smua.reset()
#-- source voltage so set the range for voltage source
keithley_instrument.smua.source.rangev = pulse_volt if pulse_volt > bias_volt else bias_volt # [V]
#-- bias
keithley_instrument.smua.source.levelv =  bias_volt # [V] 
#-- set source function
keithley_instrument.smua.source.func = keithley_instrument.smua.OUTPUT_DCVOLTS
#-- Select measure I autorange.
keithley_instrument.smua.measure.autorangei = keithley_instrument.smua.AUTORANGE_ON # (with very small current -> timeout error)
# k.smua.measure.rangei = 1e-7
# turn autozero off for sweeping or time critical measurements
keithley_instrument.smua.measure.autozero = keithley_instrument.smua.AUTOZERO_OFF
keithley_instrument.smua.measure.filter.enable = keithley_instrument.smua.FILTER_OFF 
#-- Select ASCII data format.
# k.format.data = k.format.ASCII

# -- buffer
#-- Clear buffer 1.
keithley_instrument.smua.nvbuffer1.clear()
#-- Enable append buffer mode.
keithley_instrument.smua.nvbuffer1.appendmode = 1
#-- Enable source value storage.
keithley_instrument.smua.nvbuffer1.collectsourcevalues = 1
#-- Enable source value storage.
keithley_instrument.smua.nvbuffer1.collecttimestamps = 1

        # # ======
        # # configure AD3 (gate, drain) for write
        # # ======
    # w1_period = write period -> wait time = 0 [s]
    # w2_period = w1_period - delta_tpre_tpost ; w2 must have wait time = delta_tpre_tpost 
delta_tpre_tpost = 30e-3 # [s]
n_write_cycle = 40

w1_ch_drain = 1 # 
w1_period = 500e-3 # [s]
w1_pulse_width = 50e-3 # [s]
w1_freq = 1/(w1_period) # [Hz]
w1_amplitude = pulse_volt #0.1 # pulse_volt # [V]
w1_offset = 0 # [V]
w1_percentageSymmetry =  w1_pulse_width * 100/ w1_period # [%]
secWait_1 = 0 # [s]
            
w2_ch_gate = 0
w2_period = w1_period -  delta_tpre_tpost # [s]
pulse_width_ch_2 = w1_pulse_width # [s]
w2_freq = 1/ w2_period # [Hz]
w2_amplitude = 0.8 # [V]
w2_offset = 0 # [V]
w2_percentageSymmetry = (pulse_width_ch_2 / w2_period) * 100 # pulse width = 100 ms
secWait_2 =  delta_tpre_tpost # [s]

ad3_settle_time = 0.1 # [s]
        # write
        # configure the AD3 wavegen configure (W1, W2) -> apply and stop 
logging.info("configure w1, drain for writing")
dwf.FDwfAnalogOutNodeEnableSet(hdwf, c_int(w1_ch_drain), dwfconstants.AnalogOutNodeCarrier, c_int(1))
dwf.FDwfAnalogOutNodeFunctionSet(hdwf, c_int(w1_ch_drain), dwfconstants.AnalogOutNodeCarrier, dwfconstants.funcPulse)
        # set freq for the customed signal
dwf.FDwfAnalogOutNodeFrequencySet(hdwf, c_int(w1_ch_drain), dwfconstants.AnalogOutNodeCarrier, c_double(w1_freq))
        # FDwfAnalogOutNodeSymmetrySet(HDWF hdwf, int idxChannel, AnalogOutNode node, double percentageSymmetry)
dwf.FDwfAnalogOutNodeSymmetrySet(hdwf, c_int(w1_ch_drain), dwfconstants.AnalogOutNodeCarrier, c_double(w1_percentageSymmetry))
dwf.FDwfAnalogOutOffsetSet(hdwf, c_int(w1_ch_drain), c_double(w1_offset))
dwf.FDwfAnalogOutNodeAmplitudeSet(hdwf, c_int(w1_ch_drain), dwfconstants.AnalogOutNodeCarrier, c_double(w1_amplitude))

        # FDwfAnalogOutRunSet(HDWF hdwf, int idxChannel, double secRun)
secRun =  w1_period # determine the 1 period of the signal
dwf.FDwfAnalogOutRunSet(hdwf, c_int(w1_ch_drain), c_double(secRun))
        # FDwfAnalogOutWaitSet(HDWF hdwf, int idxChannel, double secWait)
dwf.FDwfAnalogOutWaitSet(hdwf, c_int(w1_ch_drain), c_double(secWait_1))
        # FDwfAnalogOutRepeatSet(HDWF hdwf, int idxChannel, int cRepeat);
cRepeat= n_write_cycle # how many periods 
dwf.FDwfAnalogOutRepeatSet(hdwf, c_int(w1_ch_drain), c_int(cRepeat))
idle = dwfconstants.DwfAnalogOutIdleOffset
dwf.FDwfAnalogOutIdleSet(hdwf, c_int(w1_ch_drain), idle)
        # apply the configuration
        # FDwfAnalogOutConfigure(HDWF hdwf, int idxChannel, int fStart)
        # fStart – Start the instrument: 0 stop, 1 start, 3 apply.
dwf.FDwfAnalogOutConfigure(hdwf, c_int(w1_ch_drain), c_int(0))
time.sleep(ad3_settle_time)

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
dwf.FDwfAnalogOutRepeatSet(hdwf, c_int(w2_ch_gate), c_int(cRepeat))
idle = dwfconstants.DwfAnalogOutIdleOffset
dwf.FDwfAnalogOutIdleSet(hdwf, c_int(w2_ch_gate), idle)
        # FDwfAnalogOutTriggerSourceSet(HDWF hdwf, int idxChannel, TRIGSRC trigsrc)
trgsrc = dwfconstants.trigsrcAnalogOut2
dwf.FDwfAnalogOutTriggerSourceSet(hdwf, c_int(w2_ch_gate), trgsrc)
        # FDwfAnalogOutTriggerSlopeSet(HDWF hdwf, int idxChannel, DwfTriggerSlope slope)
slope = dwfconstants.DwfTriggerSlopeRise
dwf.FDwfAnalogOutTriggerSlopeSet(hdwf, c_int(w2_ch_gate), slope)
dwf.FDwfAnalogOutWaitSet(hdwf, c_int(w2_ch_gate), c_double(secWait_2))
        # apply the configuration
dwf.FDwfAnalogOutConfigure(hdwf, c_int(w2_ch_gate), c_int(0))
time.sleep(ad3_settle_time)

        # # ======
        # # Arduino board, change between read and write
        # # ======
logging.info("configure arduino mux")
            # Y2 = read phase (keithley)
            # Y3 = write phase (AD3)
arduino_bin_mux_z = 10 # (HIGH = OFF/ LOW = ON)

arduino_bin_mux_s0 = 2 # (lsb)
arduino_bin_mux_s1 = 3 #
arduino_bin_mux_s2 = 4 # (msb)

arduino_bin_mux_enable = 6 #

arduino_board = pyfirmata.Arduino('COM8')

# Open all switches
arduino_board.digital[arduino_bin_mux_enable].write(1)
time.sleep(1)

        # # ======
        # # record to file
        # # ======
file_path = "C:/Users/20245580/LabCode/Codes_For_Experiments/exp_data/20250818/pulse_exp.csv"
file_path_avg = "C:/Users/20245580/LabCode/Codes_For_Experiments/exp_data/20250818/pulse_exp_avg.csv"
                # ======
                # Prepare record file
                # ======
logging.info("Prepare record file")
field_names = ['time', 'i_channel', 'date_time', 'comment']
if os.path.exists(file_path):
        print("File exists.")
else:
        print("File not exist. create file")
        with open(file_path, 'a') as file:
                file_writer = csv.DictWriter(file, fieldnames=field_names)
                file_writer.writeheader()


field_names_avg = ['time', 'i_channel_avg', 'date_time', 'comment']
if os.path.exists(file_path_avg):
        print("File exists.")
else:
        print("File not exist. create file")
        with open(file_path_avg, 'a') as file:
                file_writer = csv.DictWriter(file, fieldnames=field_names_avg)
                file_writer.writeheader()


        # ======
        # start measurement
        # ======
logging.info("start measurement")
time_ref = time.time()

logging.info("Turn on Keithley")
keithley_settle_time = 0.1 # [s]
keithley_instrument.smua.source.output = keithley_instrument.smua.OUTPUT_ON  
time.sleep(keithley_settle_time)

logging.info("comment about the exp")
comment_exp = input("comment about exp (dg or gd): ")

try:
    # for n_exp
    nexp = 20
    sw_settle_time = 1 # [s]
    wait_between_read_and_write = 5 # [s]
    wait_between_exp = 5 # [s] = wait between write and read

    # wait for initial conds stable
    time.sleep(5)
    
    for idx_exp in range(0, nexp):
        # # read
        # logging.info("reading phase")
        # print("read phase")
        # # arduino mux connect to read configure keithely (y2)
        #         # Y0 configure
        # arduino_board.digital[arduino_bin_mux_s0].write(0)
        # arduino_board.digital[arduino_bin_mux_s1].write(1)
        # arduino_board.digital[arduino_bin_mux_s2].write(0)
        #         # close switch
        # arduino_board.digital[arduino_bin_mux_enable].write(0)
        # time.sleep(sw_settle_time)
        # # read from keithley
        # keithley_instrument.smua.source.output = keithley_instrument.smua.OUTPUT_ON
        # number_reading_pulses = 1
        # t_on = w1_pulse_width # [s]
        # t_off = 500e-3 # [s]
        #     # time.sleep(5)
        # keithley_instrument.smua.measure.nplc = 1 # [PLC], PLC = 50Hz = 20ms; nplc < ton 
        # keithley_instrument.smua.nvbuffer1.clear()
        # try:
        #     keithley_instrument.PulseVMeasureI(keithley_instrument.smua, bias_volt, pulse_volt, t_on, t_off, number_reading_pulses)
        #     logging.info(f"read successfully")
        #     # save to file
        #     cur_time = time.time()
        #     cur_datetime = datetime.now()
        #     n_samples = keithley_instrument.smua.nvbuffer1.n
        #     average = 0
        #     for i in range(0, n_samples):
        #         measured_i = keithley_instrument.smua.nvbuffer1.readings[i+1]
        #         keithely_time_stamp = keithley_instrument.smua.nvbuffer1.sourcevalues[i+1]
        #         measured_vd = keithley_instrument.smua.nvbuffer1.sourcevalues[i+1]
        #         with open(file_path, 'a') as file: 
        #                             # NOTICE: THE WHILE LOOP/ FOR LOOP INSIDE -> NO CONSTANT UPDATE TO FILE AT ALL -> NO ANIMATION
        #             file_writer = csv.DictWriter(file, fieldnames=field_names)
        #             info = {
        #                     'time':cur_time - time_ref + keithely_time_stamp,
        #                     'i_channel': measured_i,
        #                     'date_time': cur_datetime,
        #                     'comment': comment_exp + '; vg: [V]' + str(w2_amplitude) 
        #                                 + '; vd: [V]'+ str(w1_amplitude) 
        #                                 + '; delta_t: [s]' + str(delta_tpre_tpost)
        #                                 + '; n_read_points: ' + str(n_samples),    
        #                     }
        #             file_writer.writerow(info)
        #         average = average + measured_i
        #     average = average/ n_samples
        #     with open(file_path_avg, 'a') as file: 
        #             # NOTICE: THE WHILE LOOP/ FOR LOOP INSIDE -> NO CONSTANT UPDATE TO FILE AT ALL -> NO ANIMATION
        #         file_writer = csv.DictWriter(file, fieldnames=field_names_avg)
        #         info = {
        #                 'time':cur_time - time_ref,
        #                 'i_channel_avg': average,
        #                 'date_time': cur_datetime,
        #                 'comment': comment_exp + '; vg: [V]' + str(w2_amplitude) 
        #                                 + '; vd: [V]'+ str(w1_amplitude) 
        #                                 + '; delta_t: [s]' + str(delta_tpre_tpost)
        #                                 + '; n_read_points: ' + str(n_samples),    
        #                 }
        #         file_writer.writerow(info)
            
        #     # clear keithley buffer before another read

        # except Exception as e:
        #     logging.info(f"Keithley error: {e=}")
        #     logging.info(f"EXIT: {e=}")
        #     sys.exit(-1)
        
        # time.sleep(wait_between_read_and_write)
        logging.info("writing phase")
        print("writing phase")
        # write at gate, drain
        # arduino mux connect to write configure ad3 (y3)
                # Y0 configure
        arduino_board.digital[arduino_bin_mux_s0].write(1)
        arduino_board.digital[arduino_bin_mux_s1].write(1)
        arduino_board.digital[arduino_bin_mux_s2].write(0)
                # close switch
        arduino_board.digital[arduino_bin_mux_enable].write(0)
        time.sleep(sw_settle_time)
        # write to drain and gate
        # start AD3 wavegen (W1, W2)
        dwf.FDwfAnalogOutConfigure(hdwf, c_int(w2_ch_gate), c_int(1))
        time.sleep(1)
        dwf.FDwfAnalogOutConfigure(hdwf, c_int(w1_ch_drain), c_int(1))

        # wait until the AD3 finish
        sts = c_ubyte()
        wavegen_done = dwfconstants.DwfStateDone
        while sts.value != wavegen_done.value:
            dwf.FDwfAnalogOutStatus(hdwf, c_int(w2_ch_gate), byref(sts))
            time.sleep(0.5)
            logging.info(f"{sts=}")
            logging.info(f"{wavegen_done=}")

        logging.info("writing successfully")
        time.sleep(wait_between_read_and_write)
        # read
        logging.info("reading phase")
        print("read phase")
        # arduino mux connect to read configure keithely (y2)
                # Y0 configure
        arduino_board.digital[arduino_bin_mux_s0].write(0)
        arduino_board.digital[arduino_bin_mux_s1].write(1)
        arduino_board.digital[arduino_bin_mux_s2].write(0)
        #         # close switch
        arduino_board.digital[arduino_bin_mux_enable].write(0)
        time.sleep(sw_settle_time)
        # read from keithley
        keithley_instrument.smua.source.output = keithley_instrument.smua.OUTPUT_ON
        number_reading_pulses = 1
        t_on = w1_pulse_width # [s]
        t_off = 500e-3 # [s]
            # time.sleep(5)
        keithley_instrument.smua.measure.nplc = 0.1 # [PLC], PLC = 50Hz = 20ms; nplc < ton 
        keithley_instrument.smua.nvbuffer1.clear()
        try:
            keithley_instrument.PulseVMeasureI(keithley_instrument.smua, bias_volt, pulse_volt, t_on, t_off, number_reading_pulses)
            logging.info(f"read successfully")
            # save to file
            cur_time = time.time()
            cur_datetime = datetime.now()
            n_samples = keithley_instrument.smua.nvbuffer1.n
            average = 0
            for i in range(0, n_samples):
                measured_i = keithley_instrument.smua.nvbuffer1.readings[i+1]
                keithely_time_stamp = keithley_instrument.smua.nvbuffer1.sourcevalues[i+1]
                measured_vd = keithley_instrument.smua.nvbuffer1.sourcevalues[i+1]
                with open(file_path, 'a') as file: 
                                    # NOTICE: THE WHILE LOOP/ FOR LOOP INSIDE -> NO CONSTANT UPDATE TO FILE AT ALL -> NO ANIMATION
                    file_writer = csv.DictWriter(file, fieldnames=field_names)
                    info = {
                            'time':cur_time - time_ref + keithely_time_stamp,
                            'i_channel': measured_i,
                            'date_time': cur_datetime,
                            'comment': comment_exp + '; vg: [V]' + str(w2_amplitude) 
                                        + '; vd: [V]'+ str(w1_amplitude) 
                                        + '; delta_t: [s]' + str(delta_tpre_tpost)
                                        + '; pulse_width [s]: ' + str(w1_pulse_width)
                                        + '; pulse_period [s]: ' + str(w1_period)
                                        + '; n_read_points: ' + str(n_samples)
                                        + '; n_write_cycle : ' + str(n_write_cycle)
                                        + '; sw_settle_time [s]: ' + str(sw_settle_time)
                                        + '; wait_between_read_and_write [s]: ' + str(wait_between_read_and_write)
                                        + '; wait_between_exp [s]: ' + str(wait_between_exp),

                            }
                    file_writer.writerow(info)
                average = average + measured_i
            average = average/ n_samples
            with open(file_path_avg, 'a') as file: 
                    # NOTICE: THE WHILE LOOP/ FOR LOOP INSIDE -> NO CONSTANT UPDATE TO FILE AT ALL -> NO ANIMATION
                file_writer = csv.DictWriter(file, fieldnames=field_names_avg)
                info = {
                        'time':cur_time - time_ref,
                        'i_channel_avg': average,
                        'date_time': cur_datetime,
                        'comment': comment_exp + '; vg: [V]' + str(w2_amplitude) 
                                        + '; vd: [V]'+ str(w1_amplitude) 
                                        + '; delta_t: [s]' + str(delta_tpre_tpost)
                                        + '; pulse_width [s]: ' + str(w1_pulse_width)
                                        + '; pulse_period [s]: ' + str(w1_period)
                                        + '; n_read_points: ' + str(n_samples)
                                        + '; n_write_cycle : ' + str(n_write_cycle)
                                        + '; sw_settle_time [s]: ' + str(sw_settle_time)
                                        + '; wait_between_read_and_write [s]: ' + str(wait_between_read_and_write)
                                        + '; wait_between_exp [s]: ' + str(wait_between_exp),
                        }
                file_writer.writerow(info)
            
            # clear keithley buffer before another read

        except Exception as e:
            logging.info(f"Keithley error: {e=}")
            logging.info(f"EXIT: {e=}")
            sys.exit(-1)

        # wait between exp
        time.sleep(wait_between_exp)

    logging.info("MEASUREMENT FINISH")
    keithley_instrument.smua.source.output = keithley_instrument.smua.OUTPUT_OFF
                # disconnect
    arduino_board.digital[arduino_bin_mux_enable].write(1)
            # turn off the keithley
    keithley_instrument.smua.source.output = keithley_instrument.smua.OUTPUT_OFF   # turn off SMUA
            # AD3 close and reset
    dwf.FDwfAnalogOutReset(hdwf, c_int(w2_ch_gate))
    dwf.FDwfAnalogOutReset(hdwf, c_int(w1_ch_drain))
    dwf.FDwfDeviceCloseAll()

except KeyboardInterrupt:
    print(f"MEASUREMENT: EXIT KeyboardInterrupt")
    keithley_instrument.smua.source.output = keithley_instrument.smua.OUTPUT_OFF
                # disconnect
    arduino_board.digital[arduino_bin_mux_enable].write(1)
            # turn off the keithley
    keithley_instrument.smua.source.output = keithley_instrument.smua.OUTPUT_OFF   # turn off SMUA
            # AD3 close and reset
    dwf.FDwfAnalogOutReset(hdwf, c_int(w2_ch_gate))
    dwf.FDwfAnalogOutReset(hdwf, c_int(w1_ch_drain))
    dwf.FDwfDeviceCloseAll()
