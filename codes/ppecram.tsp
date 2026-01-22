-- ECRAM MEASUREMENT. v2
-- Changes
--      full measurement both negative and positive pulseing of Vg in one file
-- date 20260115
-- author Tran Le Phuong Lan
-- gate pulse (smub), fixed drain voltage (smua)
-- measure Vg, Ig, Id.

-- Connection definition
smu_drain = smua
smu_gate = smub

-- smua = drain
pulse_off_drain = 0.1
pulse_on_drain = 0.7
vdrain = 0.1

-- smub = gate
pulse_off_gate = 0
pulse_on_gate = 0.7

-- Delay between source and measurement
stime = 0.01

-- total number of source/measurement points
points = 5000

-- Update display with test info. 
        -- only 2 lines/rows
        -- Line 1, column 1 (20 characters max)
        -- Line 2, column 1 (32 characters max)
display.clear()
display.settext("PulseGateFixedDrain") 
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
smu_drain.source.levelv = vdrain 
smu_drain.source.rangev = math.max(math.abs(pulse_off_drain), math.abs(pulse_on_drain)) 
smu_drain.measure.autozero = smu_drain.AUTOZERO_OFF

smu_gate.source.output = smu_gate.OUTPUT_OFF 
smu_gate.source.func = smu_gate.OUTPUT_DCVOLTS 
smu_gate.source.levelv = 0 
smu_gate.source.rangev = math.max(math.abs(pulse_off_gate), math.abs(pulse_on_gate)) 
smu_gate.measure.autozero = smu_gate.AUTOZERO_OFF

-- display.clear()
-- display.settext("EndSource")
-- delay(2)

-- Setup a buffer to store the result(s) in and start testing. 
smu_drain.nvbuffer1.clear() 
smu_drain.nvbuffer1.appendmode = 0 
smu_drain.nvbuffer1.collecttimestamps = 1 
smu_drain.nvbuffer1.collectsourcevalues = 1 
-- smua.nvbuffer1.fillmode = FILL_WINDOW
smu_drain.nvbuffer1.fillcount = 0
smu_drain.nvbuffer1.timestampresolution = 0.01

smu_gate.nvbuffer1.clear() 
smu_gate.nvbuffer1.appendmode = 0 
smu_gate.nvbuffer1.collecttimestamps = 1 
smu_gate.nvbuffer1.collectsourcevalues = 1 
smu_gate.nvbuffer1.fillcount = 0
smu_gate.nvbuffer1.timestampresolution = 0.01

-- display.clear()
-- display.settext("EndBuff")
-- delay(2)

-- ##########################
-- PHASE ONE: 
-- Configure actions (Source, Measure) and trigger model/sequence 
  ---## actions
smu_drain.trigger.source.listv({0.1})
smu_drain.trigger.source.action = smu_drain.ENABLE 
smu_drain.trigger.measure.action = smu_drain.ENABLE
smu_drain.trigger.measure.i(smu_drain.nvbuffer1)
smu_drain.measure.nplc = 0.01
smu_drain.trigger.endpulse.action = smu_drain.SOURCE_HOLD 
smu_drain.trigger.arm.count = 1
smu_drain.trigger.count = points 
        -- The number of times the source-measure unit (SMU) iterates in 
        -- the trigger layer for any given sweep

smu_gate.trigger.source.listv({0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.7, 0.7, 0.7, 0.7, 0.7, 0.7, 0.7, 0.7, 0.7, 0.7, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0})
smu_gate.trigger.source.action = smu_gate.ENABLE
smu_gate.trigger.measure.action = smu_gate.ENABLE
-- CAN NOT MEASURE Gate current with time sensitive (~1e-8 [A]),
-- Because the current is too small, so all the timing between
-- pulisng of gate and measurment of Id will be totally WRONG.
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
        -- only change gate voltage (smub) when drain current (smua) is measured completely.

-- display.clear()
-- display.settext("EndTrigActModel")
-- delay(2)

-- Run the sweep and then turn the output off. 

smu_drain.source.output = smu_drain.OUTPUT_ON 
smu_gate.source.output = smu_gate.OUTPUT_ON

smu_drain.trigger.initiate()
smu_gate.trigger.initiate() 

waitcomplete() 

display.clear()
display.setcursor(2,1)              
display.settext("Complete phase I.")     -- Line 2 (32 characters max) 
delay(1) 
display.clear() 

-- -- ##########################
-- PHASE TWO: 
-- update some requirement
-- smub = gate
pulse_off_gate = 0
pulse_on_gate = 0
smu_gate.source.rangev = math.max(math.abs(pulse_off_gate), math.abs(pulse_on_gate)) 
-- update the voltage list of the gate voltage
smu_gate.trigger.source.listv({0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0})
smu_drain.trigger.source.listv({0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.7, 0.7, 0.7, 0.7, 0.7, 0.7, 0.7, 0.7, 0.7, 0.7, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1})

-- turn on the appendmode for internal buffer
smu_gate.nvbuffer1.appendmode = 1
smu_drain.nvbuffer1.appendmode = 1
-- reset the trigger counts to start a new measurement
smu_drain.trigger.arm.count = 1
smu_drain.trigger.count = points 
smu_gate.trigger.arm.count = 1  
smu_gate.trigger.count = points
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
        -- only change gate voltage (smub) when drain current (smua) is measured completely.
display.settext("phase II starts...")     -- Line 2 (32 characters max)         
-- continue meansuring
smu_drain.trigger.initiate()
smu_gate.trigger.initiate() 

waitcomplete() 

-- turn off the instrumen @ end of exp
smu_drain.source.output = smu_drain.OUTPUT_OFF
smu_gate.source.output = smu_gate.OUTPUT_OFF

display.clear()
display.setcursor(2,1)              
display.settext("Complete phase II.")     -- Line 2 (32 characters max) 
delay(1) 
display.clear() 

-- Update the front panel display and restore modified settings. 
display.clear()
display.setcursor(2,1)              
display.settext("COMPLETE ALL.")     -- Line 2 (32 characters max) 
delay(1) 
display.clear() 

