-- ECRAM MEASUREMENT
-- date 20260115
-- author Tran Le Phuong Lan
-- gate pulse (smub), fixed drain voltage (smua)
-- measure Vg, Ig, Id.


-- smua = drain
startv_a = 0.1
stopv_a = 0.1
vd = 0.1 -- [V]

-- smub = gate
startv_b = 0
stopv_b = 0.7

-- Delay between source and measurement
stime = 0.001

-- total number of source/measurement points
points = 1500

-- Update display with test info. 
        -- only 2 lines/rows
        -- Line 1, column 1 (20 characters max)
        -- Line 2, column 1 (32 characters max)
display.clear()
display.settext("PulseGateFixedDrain") 
--                row, column
display.setcursor(2,1)  
display.settext("MeasureIgAndId") 
delay(1) 

-- display.setcursor(1,1)
-- display.settext("Start EXP")

-- Reset trigger model 
smua.trigger.arm.stimulus = 0 -- throughout the whole program
        -- `trigger.arm.stimulus = 0` =  bypass waiting for events at the arm event detector =
        --- the SMU continues uninterrupted through the remote trigger model

smua.trigger.source.stimulus = 0 -- throughout the whole program
        -- `trigger.source.stimulus = 0` =
        -- To bypass waiting for an event, set the value of this attribute to zero (0)

smua.trigger.measure.stimulus = 0

smua.trigger.endpulse.stimulus = 0 -- throughout the whole program
        -- `trigger.endpulse.stimulus = 0` =
        -- To bypass waiting for an event, set this value of this attribute to 0

smub.trigger.arm.stimulus = 0
smub.trigger.source.stimulus = 0
smub.trigger.measure.stimulus = 0 
smub.trigger.endpulse.stimulus = 0

-- display.clear()
-- display.settext("EndRstTrig") 
-- delay(2)

-- Configure source and measure settings. 
smua.source.output = smua.OUTPUT_OFF 
smua.source.func = smua.OUTPUT_DCVOLTS 
smua.source.levelv = 0 
smua.source.rangev = math.max(math.abs(startv_a), math.abs(stopv_a)) 
smua.measure.autozero = smua.AUTOZERO_OFF

smub.source.output = smub.OUTPUT_OFF 
smub.source.func = smub.OUTPUT_DCVOLTS 
smub.source.levelv = 0 
smub.source.rangev = math.max(math.abs(startv_b), math.abs(stopv_b)) 
smub.measure.autozero = smub.AUTOZERO_OFF

-- display.clear()
-- display.settext("EndSource")
-- delay(2)

-- Setup a buffer to store the result(s) in and start testing. 
smua.nvbuffer1.clear() 
smua.nvbuffer1.appendmode = 0 
smua.nvbuffer1.collecttimestamps = 1 
smua.nvbuffer1.collectsourcevalues = 1 
-- smua.nvbuffer1.fillmode = FILL_WINDOW
smua.nvbuffer1.fillcount = 0
smua.nvbuffer1.timestampresolution = 0.001 

smub.nvbuffer1.clear() 
smub.nvbuffer1.appendmode = 0 
smub.nvbuffer1.collecttimestamps = 1 
smub.nvbuffer1.collectsourcevalues = 1 
smub.nvbuffer1.fillcount = 0
smub.nvbuffer1.timestampresolution = 0.001 

-- display.clear()
-- display.settext("EndBuff")
-- delay(2)

-- Configure actions (Source, Measure) and trigger model/sequence 
  ---## actions
smua.trigger.source.listv({vd})
smua.trigger.source.action = smua.ENABLE 
smua.trigger.measure.action = smua.ENABLE
smua.trigger.measure.i(smua.nvbuffer1)
smua.measure.nplc = 0.01
smua.trigger.endpulse.action = smua.SOURCE_HOLD 
smua.trigger.arm.count = 1
smua.trigger.count = points 
        -- The number of times the source-measure unit (SMU) iterates in 
        -- the trigger layer for any given sweep

smub.trigger.source.listv({0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0})
smub.trigger.source.action = smub.ENABLE
smub.trigger.measure.action = smub.ENABLE
smub.trigger.measure.v(smub.nvbuffer1)
smub.measure.nplc = 0.01
smub.trigger.endpulse.action = smub.SOURCE_HOLD 
smub.trigger.arm.count = 1  
smub.trigger.count = points 

-- Configure the trigger.timer[1] to set delay between source and measure 
delay_timer_a = trigger.timer[1] 
delay_timer_b = trigger.timer[2]

if (stime > 0) then 

        delay_timer_a.reset() 
        -- total number of sweep voltages (in this case, especially Vgate - smub)
        delay_timer_a.count = points
        delay_timer_a.delay = stime 
        delay_timer_a.passthrough = true
                -- `.passthrough = true` = Configure the timer to immediately output a trigger event when it is started.
        
        delay_timer_b.reset() 
        -- total number of sweep voltages (in this case, especially Vgate - smub)
        delay_timer_b.count = points
        delay_timer_b.delay = stime 
        delay_timer_b.passthrough = true
                -- `.passthrough = true` = Configure the timer to immediately output a trigger event when it is started.
end

  ---## Trigger sequence
-- arm layer
smua.trigger.arm.stimulus = 0
smub.trigger.arm.stimulus = 0
  -- smub (gate voltage) should start only when the voltage at the drain (smua) is stable
-- trigger layer
  -- source stage
smua.trigger.source.stimulus = 0
smub.trigger.source.stimulus = 0
-- trigger the delay between source and measurement
delay_timer_a.stimulus = smua.trigger.SOURCE_COMPLETE_EVENT_ID
delay_timer_b.stimulus = smub.trigger.SOURCE_COMPLETE_EVENT_ID

  -- measure stage
smua.trigger.measure.stimulus =  delay_timer_a.EVENT_ID
smub.trigger.measure.stimulus =  delay_timer_b.EVENT_ID
  -- end pulse stage
smua.trigger.endpulse.stimulus = 0
smub.trigger.endpulse.stimulus = 0
        -- only change gate voltage (smub) when drain current (smua) is measured completely.

-- display.clear()
-- display.settext("EndTrigActModel")
-- delay(2)

-- Run the sweep and then turn the output off. 

smua.source.output = smua.OUTPUT_ON 
smub.source.output = smub.OUTPUT_ON

smua.trigger.initiate()
smub.trigger.initiate() 

waitcomplete() 

smua.source.output = smua.OUTPUT_OFF 
smub.source.output = smub.OUTPUT_OFF

-- Update the front panel display and restore modified settings. 
display.clear()
display.setcursor(2,1)              
display.settext("Test complete.")     -- Line 2 (32 characters max) 
delay(1) 
display.clear() 

