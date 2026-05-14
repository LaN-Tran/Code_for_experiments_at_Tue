-- OECT PROFILING -TRANSFER CURVE MEASUREMENT
-- Changes
--      
-- date 20260514
-- author Tran Le Phuong Lan

-- # PARAMETER SETTINGS
display.clear()   

        -- smua = drain
startv_a = -0.6
stopv_a = 0.6
vd = -0.6

        -- smub = gate
startv_b = -0.5
stopv_b = 0.5

        -- Delay between source and measurement
stime = 0.01

        -- total number of source/measurement points
points = 101

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
smu_drain.measure.nplc = 0.1
smu_drain.trigger.endpulse.action = smu_drain.SOURCE_HOLD 
smu_drain.trigger.arm.count = 1
smu_drain.trigger.count = points 
        -- The number of times the source-measure unit (SMU) iterates in 
        -- the trigger layer for any given sweep

smu_gate.trigger.source.action = smu_gate.ENABLE
smu_gate.trigger.measure.action = smu_gate.ENABLE
smu_gate.trigger.measure.v(smu_gate.nvbuffer1)
smu_gate.measure.nplc = 0.1
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
	smu_gate.trigger.source.listv({-0.5, -0.49, -0.48, -0.47, -0.45999999999999996, -0.44999999999999996, -0.43999999999999995, -0.42999999999999994, -0.41999999999999993, -0.4099999999999999, -0.3999999999999999, -0.3899999999999999, -0.3799999999999999, -0.3699999999999999, -0.3599999999999999, -0.34999999999999987, -0.33999999999999986, -0.32999999999999985, -0.31999999999999984, -0.30999999999999983, -0.2999999999999998, -0.2899999999999998, -0.2799999999999998, -0.2699999999999998, -0.2599999999999998, -0.24999999999999978, -0.23999999999999977, -0.22999999999999976, -0.21999999999999975, -0.20999999999999974, -0.19999999999999973, -0.18999999999999972, -0.17999999999999972, -0.1699999999999997, -0.1599999999999997, -0.1499999999999997, -0.13999999999999968, -0.12999999999999967, -0.11999999999999966, -0.10999999999999965, -0.09999999999999964, -0.08999999999999964, -0.07999999999999963, -0.06999999999999962, -0.05999999999999961, -0.0499999999999996, -0.03999999999999959, -0.029999999999999583, -0.019999999999999574, -0.009999999999999565, 4.440892098500626e-16, 0.010000000000000453, 0.020000000000000462, 0.03000000000000047, 0.04000000000000048, 0.05000000000000049, 0.0600000000000005, 0.0700000000000005, 0.08000000000000052, 0.09000000000000052, 0.10000000000000053, 0.11000000000000054, 0.12000000000000055, 0.13000000000000056, 0.14000000000000057, 0.15000000000000058, 0.1600000000000006, 0.1700000000000006, 0.1800000000000006, 0.1900000000000006, 0.20000000000000062, 0.21000000000000063, 0.22000000000000064, 0.23000000000000065, 0.24000000000000066, 0.25000000000000067, 0.2600000000000007, 0.2700000000000007, 0.2800000000000007, 0.2900000000000007, 0.3000000000000007, 0.3100000000000007, 0.32000000000000073, 0.33000000000000074, 0.34000000000000075, 0.35000000000000075, 0.36000000000000076, 0.3700000000000008, 0.3800000000000008, 0.3900000000000008, 0.4000000000000008, 0.4100000000000008, 0.4200000000000008, 0.4300000000000008, 0.44000000000000083, 0.45000000000000084, 0.46000000000000085, 0.47000000000000086, 0.48000000000000087, 0.4900000000000009, 0.5000000000000009})
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
	smu_gate.trigger.source.listv({0.5, 0.49, 0.48, 0.47, 0.45999999999999996, 0.44999999999999996, 0.43999999999999995, 0.42999999999999994, 0.41999999999999993, 0.4099999999999999, 0.3999999999999999, 0.3899999999999999, 0.3799999999999999, 0.3699999999999999, 0.3599999999999999, 0.34999999999999987, 0.33999999999999986, 0.32999999999999985, 0.31999999999999984, 0.30999999999999983, 0.2999999999999998, 0.2899999999999998, 0.2799999999999998, 0.2699999999999998, 0.2599999999999998, 0.24999999999999978, 0.23999999999999977, 0.22999999999999976, 0.21999999999999975, 0.20999999999999974, 0.19999999999999973, 0.18999999999999972, 0.17999999999999972, 0.1699999999999997, 0.1599999999999997, 0.1499999999999997, 0.13999999999999968, 0.12999999999999967, 0.11999999999999966, 0.10999999999999965, 0.09999999999999964, 0.08999999999999964, 0.07999999999999963, 0.06999999999999962, 0.05999999999999961, 0.0499999999999996, 0.03999999999999959, 0.029999999999999583, 0.019999999999999574, 0.009999999999999565, -4.440892098500626e-16, -0.010000000000000453, -0.020000000000000462, -0.03000000000000047, -0.04000000000000048, -0.05000000000000049, -0.0600000000000005, -0.0700000000000005, -0.08000000000000052, -0.09000000000000052, -0.10000000000000053, -0.11000000000000054, -0.12000000000000055, -0.13000000000000056, -0.14000000000000057, -0.15000000000000058, -0.1600000000000006, -0.1700000000000006, -0.1800000000000006, -0.1900000000000006, -0.20000000000000062, -0.21000000000000063, -0.22000000000000064, -0.23000000000000065, -0.24000000000000066, -0.25000000000000067, -0.2600000000000007, -0.2700000000000007, -0.2800000000000007, -0.2900000000000007, -0.3000000000000007, -0.3100000000000007, -0.32000000000000073, -0.33000000000000074, -0.34000000000000075, -0.35000000000000075, -0.36000000000000076, -0.3700000000000008, -0.3800000000000008, -0.3900000000000008, -0.4000000000000008, -0.4100000000000008, -0.4200000000000008, -0.4300000000000008, -0.44000000000000083, -0.45000000000000084, -0.46000000000000085, -0.47000000000000086, -0.48000000000000087, -0.4900000000000009, -0.5000000000000009})
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


