import time
import logging

    # # ======
    # # Logger
    # # ======
# init logger
format = "%(asctime)s: %(message)s"
log_file_path = 'example.log'
logging.basicConfig(format=format, level=logging.INFO,  
                        datefmt="%H:%M:%S", filename= log_file_path, filemode= 'w')

read_duration = 1

try:
    while True:

        # while loop for reading period with SMUA -> save to file
        start_time = time.time()
        current_time = time.time()
        while (current_time - start_time) < read_duration:
            try:
                logging.info("reading...")
                logging.info(f"{current_time=}")
                logging.info(f"{start_time=}")
                        
            except Exception as CatchError:
                logging.info("ERROR: keithley measure function error")
                logging.info(f"{CatchError=}")
            
            current_time = time.time()
        # Your main loop logic here
        logging.info("outside reading.")
        time.sleep(0.5)
except KeyboardInterrupt:
    print("\nCtrl+C detected. Exiting gracefully.")