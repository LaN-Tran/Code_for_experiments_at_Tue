-- OECT PROFILING -OUTPUT MEASUREMENT
-- Changes
--      
-- date 20260514
-- author Tran Le Phuong Lan
-- gate pulse (smub), fixed drain voltage (smua)
-- measure sweep Vds, measure Ids, fixed Vgs.

-- Clear the front panel display then prompt for input parameters if missing. 
-- # PARAMETER SETTINGS
display.clear()   
        -- parameters for vds sweep
start_vd = -0.5
stop_vd = 0
        -- delay between source-measure point -> decide the time stime in the scan rate [V/s]: delta_vd/ stime
stime = 0.01
        -- number of points in the sweep
points = 51
        -- parameters for vgs
vgs = 0.0
        -- number of sweeps
number_of_sweeps = 3

-- Update display with test info. 
display.settext("SweepVLinMeasureI")  -- Line 1 (20 characters max) 

-- choose the channel
smu_drain = smua
smu_gate = smub

-- make sure all channels are off
smu_drain.source.output = smu_drain.OUTPUT_OFF 
smu_gate.source.output = smu_gate.OUTPUT_OFF
-- Configure source and measure settings. 
smu_drain.source.func = smu_drain.OUTPUT_DCVOLTS 
smu_drain.source.levelv = 0
smu_drain.source.rangev = math.max(math.abs(start_vd), math.abs(stop_vd)) 
smu_drain.measure.autozero = smu_drain.AUTOZERO_OFF
smu_drain.measure.autorangei = smu_drain.AUTORANGE_ON
-- Setup a buffer to store the result(s) in and start testing. 
smu_drain.nvbuffer1.clear() 
smu_drain.nvbuffer1.appendmode = 1
        -- 1: Append mode on; appends new measurement data to the present buffer content
smu_drain.nvbuffer1.collecttimestamps = 1 
smu_drain.nvbuffer1.collectsourcevalues = 1 
smu_drain.nvbuffer1.fillcount = 0
        -- smua.nvbuffer1.fillmode = FILL_WINDOW
smu_drain.nvbuffer1.timestampresolution = 0.001 

-- Reset trigger model 
smu_drain.trigger.arm.stimulus = 0 
smu_drain.trigger.source.stimulus = 0 
smu_drain.trigger.measure.stimulus = 0 
smu_drain.trigger.endpulse.stimulus = 0 
smu_drain.trigger.arm.count = 1 

-- Configure the source action 
smu_drain.trigger.source.action = smu_drain.ENABLE 
smu_drain.trigger.endpulse.action = smu_drain.SOURCE_HOLD 
-- Configure the measure action 
smu_drain.trigger.measure.i(smu_drain.nvbuffer1) 
smu_drain.trigger.measure.action = smu_drain.ENABLE 
smu_drain.measure.nplc = 0.1

-- Configure the delay 
if (stime > 0) then 
        trigger.timer[1].reset() 
        trigger.timer[1].delay = stime 
        trigger.timer[1].passthrough = false
                -- the timer does not generate a trigger event until after the first delay elapses.
        smu_drain.trigger.measure.stimulus = trigger.timer[1].EVENT_ID
        trigger.timer[1].stimulus = smu_drain.trigger.SOURCE_COMPLETE_EVENT_ID 
end

-- Configure the sweep count 
smu_drain.trigger.count = points 

-- set the fixed gate voltage, turn on the gate voltage
smu_gate.source.func = smu_gate.OUTPUT_DCVOLTS
smu_gate.source.levelv = vgs
smu_gate.source.output = smu_gate.OUTPUT_ON

-- turn on the drain voltage for signal voltage
smu_drain.source.output = smu_drain.OUTPUT_ON

-- # For loop 
for i=1, number_of_sweeps do
        -- ##########################
        -- FORWARD SWEEP 
	smu_drain.trigger.source.listv({-0.5, -0.49, -0.48, -0.47, -0.45999999999999996, -0.44999999999999996, -0.43999999999999995, -0.42999999999999994, -0.41999999999999993, -0.4099999999999999, -0.3999999999999999, -0.3899999999999999, -0.3799999999999999, -0.3699999999999999, -0.3599999999999999, -0.34999999999999987, -0.33999999999999986, -0.32999999999999985, -0.31999999999999984, -0.30999999999999983, -0.2999999999999998, -0.2899999999999998, -0.2799999999999998, -0.2699999999999998, -0.2599999999999998, -0.24999999999999978, -0.23999999999999977, -0.22999999999999976, -0.21999999999999975, -0.20999999999999974, -0.19999999999999973, -0.18999999999999972, -0.17999999999999972, -0.1699999999999997, -0.1599999999999997, -0.1499999999999997, -0.13999999999999968, -0.12999999999999967, -0.11999999999999966, -0.10999999999999965, -0.09999999999999964, -0.08999999999999964, -0.07999999999999963, -0.06999999999999962, -0.05999999999999961, -0.0499999999999996, -0.03999999999999959, -0.029999999999999583, -0.019999999999999574, -0.009999999999999565, 4.440892098500626e-16})
        smu_drain.trigger.initiate()
        waitcomplete() 

        display.clear()
        display.setcursor(2,1)              
        display.settext("Complete phase I.")     -- Line 2 (32 characters max) 
        delay(1) 
        display.clear() 

        -- ##########################
        -- BACKWARD SWEEP  
	smu_drain.trigger.source.listv({0.0, -0.01, -0.02, -0.03, -0.04, -0.05, -0.06, -0.07, -0.08, -0.09, -0.1, -0.11, -0.12, -0.13, -0.14, -0.15, -0.16, -0.17, -0.18, -0.19, -0.2, -0.21, -0.22, -0.23, -0.24, -0.25, -0.26, -0.27, -0.28, -0.29, -0.3, -0.31, -0.32, -0.33, -0.34, -0.35000000000000003, -0.36, -0.37, -0.38, -0.39, -0.4, -0.41000000000000003, -0.42, -0.43, -0.44, -0.45, -0.46, -0.47000000000000003, -0.48, -0.49, -0.5})
        -- continue meansuring
        smu_drain.trigger.initiate()
        waitcomplete()

        display.clear()
        display.setcursor(2,1)              
        display.settext("Complete phase II.")     -- Line 2 (32 characters max) 
        delay(1) 
        display.clear() 
        
end
-- # For loop end 

-- turn off the instrumen @ end of exp
smu_drain.source.output = smu_drain.OUTPUT_OFF
smu_gate.source.output = smu_gate.OUTPUT_OFF


-- Update the front panel display and restore modified settings. 
display.clear()
display.setcursor(2,1)              
display.settext("COMPLETE ALL.")     -- Line 2 (32 characters max) 
delay(1) 
display.clear() 

