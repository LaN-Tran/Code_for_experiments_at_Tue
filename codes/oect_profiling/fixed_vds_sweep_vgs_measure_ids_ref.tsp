-- OECT PROFILING -TRANSFER CURVE MEASUREMENT
-- Changes
--      
-- date 20260514
-- author Tran Le Phuong Lan

-- # PARAMETER SETTINGS
display.clear()   

        -- smua = drain
startv_a = 0.05
stopv_a = 0.05
vd = 0.05 -- [V]

        -- smub = gate
startv_b = 0
stopv_b = 0.7

        -- Delay between source and measurement
stime = 0.01

        -- total number of source/measurement points
points = 10000

        -- number of sweeps
number_of_sweeps = 3

-- choose the channel
smu_drain = smua
smu_gate = smub
-- Update display with test info. 
        -- only 2 lines/rows
        -- Line 1, column 1 (20 characters max)
        -- Line 2, column 1 (32 characters max)
display.clear()
display.settext("FixedVdSweepVg")  -- Line 1 (20 characters max)
--                row, column
display.setcursor(2,1)  
display.settext("MeasureId") 
delay(1) 

-- display.setcursor(1,1)
-- display.settext("Start EXP")

-- Reset trigger model 
smu_drain.trigger.arm.stimulus = 0 -- throughout the whole program
        -- `trigger.arm.stimulus = 0` =  bypass waiting for events at the arm event detector =
        --- the SMU continues uninterrupted through the remote trigger model

smu_drain.trigger.source.stimulus = 0 -- throughout the whole program
        -- `trigger.source.stimulus = 0` =
        -- To bypass waiting for an event, set the value of this attribute to zero (0)

smu_drain.trigger.measure.stimulus = 0

smu_drain.trigger.endpulse.stimulus = 0 -- throughout the whole program
        -- `trigger.endpulse.stimulus = 0` =
        -- To bypass waiting for an event, set this value of this attribute to 0

smu_gate.trigger.arm.stimulus = 0
smu_gate.trigger.source.stimulus = 0
smu_gate.trigger.measure.stimulus = 0 
smu_gate.trigger.endpulse.stimulus = 0

-- display.clear()
-- display.settext("EndRstTrig") 
-- delay(2)

-- Configure source and measure settings. 
smu_drain.source.output = smu_drain.OUTPUT_OFF 
smu_drain.source.func = smu_drain.OUTPUT_DCVOLTS 
smu_drain.source.levelv = 0 
smu_drain.source.rangev = math.max(math.abs(startv_a), math.abs(stopv_a)) 
smu_drain.measure.autozero = smu_drain.AUTOZERO_OFF
smu_drain.measure.autorangei = smu_drain.AUTORANGE_ON

smu_gate.source.output = smu_gate.OUTPUT_OFF 
smu_gate.source.func = smu_gate.OUTPUT_DCVOLTS 
smu_gate.source.levelv = 0 
smu_gate.source.rangev = math.max(math.abs(startv_b), math.abs(stopv_b)) 
smu_gate.measure.autozero = smu_gate.AUTOZERO_OFF
smu_gate.measure.autorangei = smu_gate.AUTORANGE_ON
-- display.clear()
-- display.settext("EndSource")
-- delay(2)

-- Setup a buffer to store the result(s) in and start testing. 
smu_drain.nvbuffer1.clear() 
smu_drain.nvbuffer1.appendmode = 1
smu_drain.nvbuffer1.collecttimestamps = 1 
smu_drain.nvbuffer1.collectsourcevalues = 1 
-- smua.nvbuffer1.fillmode = FILL_WINDOW
smu_drain.nvbuffer1.fillcount = 0
smu_drain.nvbuffer1.timestampresolution = 0.001 

smu_gate.nvbuffer1.clear() 
smu_gate.nvbuffer1.appendmode = 1
smu_gate.nvbuffer1.collecttimestamps = 1 
smu_gate.nvbuffer1.collectsourcevalues = 1 
smu_gate.nvbuffer1.fillcount = 0
smu_gate.nvbuffer1.timestampresolution = 0.001 

-- display.clear()
-- display.settext("EndBuff")
-- delay(2)

-- Configure actions (Source, Measure) and trigger model/sequence 
  ---## actions
smu_drain.trigger.source.listv({vd})
smu_drain.trigger.source.action = smu_drain.ENABLE
smu_drain.trigger.measure.action = smu_drain.ENABLE
smu_drain.trigger.measure.i(smu_drain.nvbuffer1)
smu_drain.measure.nplc = 0.01
smu_drain.trigger.endpulse.action = smu_drain.SOURCE_HOLD 
smu_drain.trigger.arm.count = 1
smu_drain.trigger.count = points 
        -- The number of times the source-measure unit (SMU) iterates in 
        -- the trigger layer for any given sweep

smu_gate.trigger.source.action = smu_gate.ENABLE
smu_gate.trigger.measure.action = smu_gate.ENABLE
smu_gate.trigger.measure.v(smu_gate.nvbuffer1)
smu_gate.measure.nplc = 0.01
smu_gate.trigger.endpulse.action = smu_gate.SOURCE_HOLD
smu_gate.trigger.arm.count = 1  
smu_gate.trigger.count = points 

-- Configure the trigger.timer[1] to set delay between source and measure 
delay_timer_a = trigger.timer[1] 
delay_timer_b = trigger.timer[2]

if (stime > 0) then 

        delay_timer_a.reset() 
        -- total number of sweep voltages (in this case, especially Vgate - smub)
        delay_timer_a.count = points
        delay_timer_a.delay = stime 
        delay_timer_a.passthrough = false
                -- `.passthrough = true` = Configure the timer to immediately output a trigger event when it is started.
        
        delay_timer_b.reset() 
        -- total number of sweep voltages (in this case, especially Vgate - smub)
        delay_timer_b.count = points
        delay_timer_b.delay = stime 
        delay_timer_b.passthrough = false
                -- `.passthrough = true` = Configure the timer to immediately output a trigger event when it is started.
end

  ---## Trigger sequence
-- arm layer
smu_drain.trigger.arm.stimulus = 0
smu_gate.trigger.arm.stimulus = 0
  -- smub (gate voltage) should start only when the voltage at the drain (smua) is stable
-- trigger layer
  -- source stage
smu_drain.trigger.source.stimulus = 0
smu_gate.trigger.source.stimulus = 0
-- trigger the delay between source and measurement
delay_timer_a.stimulus = smu_drain.trigger.SOURCE_COMPLETE_EVENT_ID
delay_timer_b.stimulus = smu_gate.trigger.SOURCE_COMPLETE_EVENT_ID

  -- measure stage
smu_drain.trigger.measure.stimulus =  delay_timer_a.EVENT_ID
smu_gate.trigger.measure.stimulus =  delay_timer_b.EVENT_ID
  -- end pulse stage
smu_drain.trigger.endpulse.stimulus = 0
smu_gate.trigger.endpulse.stimulus = 0

-- display.clear()
-- display.settext("EndTrigActModel")
-- delay(2)

-- Run the sweep and then turn the output off. 

smu_drain.source.output = smu_drain.OUTPUT_ON 
smu_gate.source.output = smu_gate.OUTPUT_ON

for i=1, number_of_sweeps do
        -- ##########################
        -- FORWARD SWEEP 
	smu_gate.trigger.source.listv({0.0, 0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09, 0.1, 0.11, 0.12, 0.13, 0.14, 0.15, 0.16, 0.17, 0.18, 0.19, 0.2, 0.21, 0.22, 0.23, 0.24, 0.25, 0.26, 0.27, 0.28, 0.29, 0.3, 0.31, 0.32, 0.33, 0.34, 0.35000000000000003, 0.36, 0.37, 0.38, 0.39, 0.4, 0.41000000000000003, 0.42, 0.43, 0.44, 0.45, 0.46, 0.47000000000000003, 0.48, 0.49, 0.5, 0.51, 0.52, 0.53, 0.54, 0.55, 0.56, 0.5700000000000001, 0.58, 0.59, 0.6, 0.61, 0.62, 0.63, 0.64, 0.65, 0.66, 0.67, 0.68, 0.6900000000000001, 0.7000000000000001})
        smu_drain.trigger.initiate()
        smu_gate.trigger.initiate()
        waitcomplete() 

        display.clear()
        display.setcursor(2,1)              
        display.settext("Complete phase I.")     -- Line 2 (32 characters max) 
        delay(1) 
        display.clear() 

        -- ##########################
        -- BACKWARD SWEEP  
	smu_gate.trigger.source.listv({0.7, 0.69, 0.6799999999999999, 0.6699999999999999, 0.6599999999999999, 0.6499999999999999, 0.6399999999999999, 0.6299999999999999, 0.6199999999999999, 0.6099999999999999, 0.5999999999999999, 0.5899999999999999, 0.5799999999999998, 0.5699999999999998, 0.5599999999999998, 0.5499999999999998, 0.5399999999999998, 0.5299999999999998, 0.5199999999999998, 0.5099999999999998, 0.4999999999999998, 0.48999999999999977, 0.47999999999999976, 0.46999999999999975, 0.45999999999999974, 0.44999999999999973, 0.4399999999999997, 0.4299999999999997, 0.4199999999999997, 0.4099999999999997, 0.3999999999999997, 0.3899999999999997, 0.37999999999999967, 0.36999999999999966, 0.35999999999999965, 0.34999999999999964, 0.33999999999999964, 0.3299999999999996, 0.3199999999999996, 0.3099999999999996, 0.2999999999999996, 0.2899999999999996, 0.2799999999999996, 0.2699999999999996, 0.25999999999999956, 0.24999999999999956, 0.23999999999999955, 0.22999999999999954, 0.21999999999999953, 0.20999999999999952, 0.1999999999999995, 0.1899999999999995, 0.1799999999999995, 0.16999999999999948, 0.15999999999999948, 0.14999999999999947, 0.13999999999999946, 0.12999999999999945, 0.11999999999999944, 0.10999999999999943, 0.09999999999999942, 0.08999999999999941, 0.0799999999999994, 0.0699999999999994, 0.05999999999999939, 0.04999999999999938, 0.03999999999999937, 0.02999999999999936, 0.01999999999999935, 0.009999999999999343, -6.661338147750939e-16})
        -- continue meansuring
        smu_drain.trigger.initiate()
        smu_gate.trigger.initiate()
        waitcomplete()

        display.clear()
        display.setcursor(2,1)              
        display.settext("Complete phase II.")     -- Line 2 (32 characters max) 
        delay(1) 
        display.clear() 
        
end

smu_drain.source.levelv = 0 
smu_gate.source.levelv = 0 
smu_drain.source.output = smu_drain.OUTPUT_OFF 
smu_gate.source.output = smu_gate.OUTPUT_OFF

-- Update the front panel display and restore modified settings. 
display.clear()
display.setcursor(2,1)              
display.settext("COMPLETE ALL.")     -- Line 2 (32 characters max) 
delay(1) 
display.clear() 


