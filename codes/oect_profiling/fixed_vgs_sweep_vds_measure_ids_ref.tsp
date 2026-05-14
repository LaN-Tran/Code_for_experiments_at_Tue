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
start_vd = 0.05
stop_vd = 0.7
        -- delay between source-measure point -> decide the time stime in the scan rate [V/s]: delta_vd/ stime
stime = 0.01
        -- number of points in the sweep
points = 10000
        -- parameters for vgs
vgs = 0
        -- number of sweeps
number_of_sweeps = 1

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
smu_drain.measure.nplc = 0.01

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
        smu_drain.trigger.source.listv({0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.7, 0.7, 0.7, 0.7, 0.7, 0.7, 0.7, 0.7, 0.7, 0.7, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05})
        smu_drain.trigger.initiate()
        waitcomplete() 

        display.clear()
        display.setcursor(2,1)              
        display.settext("Complete phase I.")     -- Line 2 (32 characters max) 
        delay(1) 
        display.clear() 

        -- ##########################
        -- BACKWARD SWEEP  
        smu_drain.trigger.source.listv({0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.7, 0.7, 0.7, 0.7, 0.7, 0.7, 0.7, 0.7, 0.7, 0.7, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0})
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

