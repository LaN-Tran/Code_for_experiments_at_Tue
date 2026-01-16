
# **NOTE**

1. **All the codes are in folder `./codes`**: - codes to automate: SMU Keithley, Oscilloscope, Arduino - pyfirmata

2. **Pyfirmata** only fits for python <= 3.10. If higher, can not use library

3. **The downgraded python version** in conda virtual environment will affect all the already installed packages (e.g numpy, pandas, matplotlib, etc). If needed to downgrade the python version, **MUST CREATE A NEW CONDA ENV** with the downgraded python version.

4. The setup for using the **Combination of files to automate STDP measurement, processing and recording (all works, V2)** in folder `codes/`

- Arduino 5v - MUX1 (74HC4051) VCC + MUX2 (74HC4051) VCC

- Arduino GND - MUX1 (74HC4051) GND + MUX2 (74HC4051) GND

- MUX1/2 (74HC4051) z - SMUB/Device gate  

5. About the keithley `.tsp`, internal buffer (`smu.nvbuffer1`, `smu.nvbuffer2`), and `smu.trigger.source.listv({})`: (NOTE: the term `rbuffer` in Keithley 2600B series code manual = `smu.nvbuffer1/2`; `smu` = `smuA` or `smuB`)

- why do we need these information? in order to make fast and time accurate measurement using `tsp` code.
    
- the internal buffer is actually very big (> 10000 samples). 
        
- There is a limit of how many values in the `smu.trigger.source.listv({...})` are allowed, around 900 values.

- **Misassumption**: the number of values in `smu.trigger.source.listv({...})` determines the maximum values to recorded samples by using `smua.trigger.measure...` or/and `smub.trigger.measure...`. 

    - **The correct way** is: 
    
    that the **number of points set for `smu.trigger.count` (= the total number of measurements made by `smu.trigger.measure.i(smu.nvbuffer1)` or `smu.trigger.measure.v(smu.nvbuffer1)` or similar, only if `smu.trigger.measure.action = smu.ENABLE`)** is limited by the max number of samples stored in the internal buffer. (`./SMU_triggering_syn_model.png`)
    
    the **shape/list of the voltage output** is limited by the max number of samples `smu.trigger.source.listv({...})`. 
    
    **If number of values set for `smua.trigger.count` >> number of values in `smu.trigger.source.listv({...})`**, then the voltage shape/list in `smu.trigger.source.listv({...})` is repeated until the value set for `smua.trigger.count` is reached.  