-- OECT PROFILING -OUTPUT MEASUREMENT
-- Changes
--      
-- date 20260514
-- author Tran Le Phuong Lan
-- gate pulse (smub), fixed drain voltage (smua)
-- measure sweep Vds, measure Ids, fixed Vgs.

-- Clear the front panel display then prompt for input parameters if missing. 
-- # PARAMETER SETTINGS
-- display.clear()   
        -- parameters for vds sweep
start_vd = 0.8
stop_vd = 0
        -- delay between source-measure point -> decide the time stime in the scan rate [V/s]: delta_vd/ stime
stime = 0.01
        -- number of points in the sweep
points_str = 1455
        -- parameters for vgs
vgs = -0.1
        -- number of sweeps
number_of_sweeps = 2

-- Update display with test info. 
-- display.settext("SweepVLinMeasureI")  -- Line 1 (20 characters max) 

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
smu_drain.trigger.count = points_str 

-- set the fixed gate voltage, turn on the gate voltage
smu_gate.source.func = smu_gate.OUTPUT_DCVOLTS
smu_gate.source.levelv = vgs
smu_gate.source.output = smu_gate.OUTPUT_ON

-- turn on the drain voltage for signal voltage
smu_drain.source.output = smu_drain.OUTPUT_ON

-- PREPARE THE SWEEP LIST
volt_offset = 5e-05
sweeplist_start = {}
vstart = 0
vstop = start_vd
for i = 0, points_str-1 do
    sweeplist_start[i+1] = vstart + (vstop - vstart) * i / (points_str - 1)
end

sweeplist_bw_1 = {}
vstart = start_vd
vstop = 0 + volt_offset
points_bw_1 = 1455
for i = 0, points_bw_1-1 do
    sweeplist_bw_1[i+1] = vstart + (vstop - vstart) * i / (points_bw_1 - 1)
end

sweeplist_bw_2 = {}
vstart = 0 + volt_offset
vstop = -start_vd
points_bw_2 = 1455
for i = 0, points_bw_2-1 do
    sweeplist_bw_2[i+1] = vstart + (vstop - vstart) * i / (points_bw_2 - 1)
end

sweeplist_fw_1 = {}
vstart = -start_vd
vstop = 0 + volt_offset
points_fw_1 = 1455
for i = 0, points_fw_1-1 do
    sweeplist_fw_1[i+1] = vstart + (vstop - vstart) * i / (points_fw_1 - 1)
end

sweeplist_fw_2 = {}
vstart = 0 + volt_offset
vstop = start_vd
points_fw_2 = 1455
for i = 0, points_fw_1-1 do
    sweeplist_fw_2[i+1] = vstart + (vstop - vstart) * i / (points_fw_2 - 1)
end

sweeplist_end = {}
vstart = start_vd
vstop = 0 + volt_offset
points_end = 1456
for i = 0, points_end-1 do
    sweeplist_end[i+1] = vstart + (vstop - vstart) * i / (points_end - 1)
end

-- START MEASUREMENT
-- ##########################
-- start sweep
smu_drain.trigger.source.listv(sweeplist_start)
smu_drain.trigger.initiate()
waitcomplete() 

-- display.clear()
display.setcursor(2,1)              
-- display.settext("Fini II Fw Pos")     -- Line 2 (32 characters max) 
delay(1) 
-- display.clear()
-- # For loop 
for i=1, number_of_sweeps do
        -- ##########################
        -- BACKWARD SWEEP
        smu_drain.trigger.count = points_bw_1
	smu_drain.trigger.source.listv(sweeplist_bw_1)
        smu_drain.trigger.initiate()
        waitcomplete()
        
        smu_drain.trigger.count = points_bw_2
	smu_drain.trigger.source.listv(sweeplist_bw_2)
        smu_drain.trigger.initiate()
        waitcomplete()

        display.clear()
        display.setcursor(2,1)              
        display.settext("Fini BW")     -- Line 2 (32 characters max) 
        delay(1)  

        -- ##########################
        -- FORWARD SWEEP 
        smu_drain.trigger.count = points_fw_1
	smu_drain.trigger.source.listv(sweeplist_fw_1)
        -- continue meansuring
        smu_drain.trigger.initiate()
        waitcomplete()

        smu_drain.trigger.count = points_fw_2
	smu_drain.trigger.source.listv(sweeplist_fw_2)
        -- continue meansuring
        smu_drain.trigger.initiate()
        waitcomplete()

        display.clear()
        display.setcursor(2,1)              
        display.settext("Fini FW")     -- Line 2 (32 characters max) 
        delay(1) 
        
end
-- # For loop end 
-- ##########################
-- end sweep 
smu_drain.trigger.count = points_end
smu_drain.trigger.source.listv(sweeplist_end)
-- continue meansuring
smu_drain.trigger.initiate()
waitcomplete()

-- turn off the instrumen @ end of exp
smu_drain.source.output = smu_drain.OUTPUT_OFF
smu_gate.source.output = smu_gate.OUTPUT_OFF


-- Update the front panel display and restore modified settings. 
display.setcursor(2,1)
display.clear()         
display.settext("COMPLETE ALL.")     -- Line 2 (32 characters max) 
delay(1) 


