-- OECT PROFILING -TRANSFER CURVE MEASUREMENT
-- Changes
--      
-- date 20260514
-- author Tran Le Phuong Lan

-- # PARAMETER SETTINGS
display.clear()   

        -- smua = drain
startv_a = -0.3
stopv_a = 0.1
vd = 0.10000000000000003

        -- smub = gate
startv_b = -0.6
stopv_b = 0.6

        -- Delay between source and measurement
stime = 0.01

        -- total number of source/measurement points
points = 121

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
smu_drain.source.levelv = vd
smu_drain.trigger.source.action = smu_drain.DISABLE
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
-- smu_gate.trigger.measure.v(smu_gate.nvbuffer1)
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
-- delay_timer_a.stimulus = smu_drain.trigger.SOURCE_COMPLETE_EVENT_ID
delay_timer_b.stimulus = smu_gate.trigger.SOURCE_COMPLETE_EVENT_ID

  -- measure stage
smu_drain.trigger.measure.stimulus =  delay_timer_b.EVENT_ID
smu_gate.trigger.measure.stimulus =  0
  -- end pulse stage
smu_drain.trigger.endpulse.stimulus = 0
smu_gate.trigger.endpulse.stimulus = smu_drain.trigger.MEASURE_COMPLETE_EVENT_ID

-- display.clear()
-- display.settext("EndTrigActModel")
-- delay(2)

-- Run the sweep and then turn the output off. 

smu_drain.source.output = smu_drain.OUTPUT_ON 
smu_gate.source.output = smu_gate.OUTPUT_ON

for i=1, number_of_sweeps do
        -- ##########################
        -- FORWARD SWEEP 
	smu_gate.trigger.source.listv({-0.6, -0.59, -0.58, -0.57, -0.5599999999999999, -0.5499999999999999, -0.5399999999999999, -0.5299999999999999, -0.5199999999999999, -0.5099999999999999, -0.4999999999999999, -0.4899999999999999, -0.47999999999999987, -0.46999999999999986, -0.45999999999999985, -0.44999999999999984, -0.43999999999999984, -0.4299999999999998, -0.4199999999999998, -0.4099999999999998, -0.3999999999999998, -0.3899999999999998, -0.3799999999999998, -0.3699999999999998, -0.35999999999999976, -0.34999999999999976, -0.33999999999999975, -0.32999999999999974, -0.31999999999999973, -0.3099999999999997, -0.2999999999999997, -0.2899999999999997, -0.2799999999999997, -0.2699999999999997, -0.2599999999999997, -0.24999999999999967, -0.23999999999999966, -0.22999999999999965, -0.21999999999999964, -0.20999999999999963, -0.19999999999999962, -0.1899999999999996, -0.1799999999999996, -0.1699999999999996, -0.1599999999999996, -0.14999999999999958, -0.13999999999999957, -0.12999999999999956, -0.11999999999999955, -0.10999999999999954, -0.09999999999999953, -0.08999999999999952, -0.07999999999999952, -0.06999999999999951, -0.0599999999999995, -0.04999999999999949, -0.03999999999999948, -0.02999999999999947, -0.019999999999999463, -0.009999999999999454, 5.551115123125783e-16, 0.010000000000000564, 0.020000000000000573, 0.030000000000000582, 0.04000000000000059, 0.0500000000000006, 0.06000000000000061, 0.07000000000000062, 0.08000000000000063, 0.09000000000000064, 0.10000000000000064, 0.11000000000000065, 0.12000000000000066, 0.13000000000000067, 0.14000000000000068, 0.1500000000000007, 0.1600000000000007, 0.1700000000000007, 0.18000000000000071, 0.19000000000000072, 0.20000000000000073, 0.21000000000000074, 0.22000000000000075, 0.23000000000000076, 0.24000000000000077, 0.2500000000000008, 0.2600000000000008, 0.2700000000000008, 0.2800000000000008, 0.2900000000000008, 0.3000000000000008, 0.31000000000000083, 0.32000000000000084, 0.33000000000000085, 0.34000000000000086, 0.35000000000000087, 0.3600000000000009, 0.3700000000000009, 0.3800000000000009, 0.3900000000000009, 0.4000000000000009, 0.4100000000000009, 0.42000000000000093, 0.43000000000000094, 0.44000000000000095, 0.45000000000000095, 0.46000000000000096, 0.470000000000001, 0.480000000000001, 0.490000000000001, 0.500000000000001, 0.510000000000001, 0.520000000000001, 0.530000000000001, 0.540000000000001, 0.550000000000001, 0.560000000000001, 0.5700000000000011, 0.5800000000000011, 0.5900000000000011, 0.6000000000000011})
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
	smu_gate.trigger.source.listv({0.6, 0.59, 0.58, 0.57, 0.5599999999999999, 0.5499999999999999, 0.5399999999999999, 0.5299999999999999, 0.5199999999999999, 0.5099999999999999, 0.4999999999999999, 0.4899999999999999, 0.47999999999999987, 0.46999999999999986, 0.45999999999999985, 0.44999999999999984, 0.43999999999999984, 0.4299999999999998, 0.4199999999999998, 0.4099999999999998, 0.3999999999999998, 0.3899999999999998, 0.3799999999999998, 0.3699999999999998, 0.35999999999999976, 0.34999999999999976, 0.33999999999999975, 0.32999999999999974, 0.31999999999999973, 0.3099999999999997, 0.2999999999999997, 0.2899999999999997, 0.2799999999999997, 0.2699999999999997, 0.2599999999999997, 0.24999999999999967, 0.23999999999999966, 0.22999999999999965, 0.21999999999999964, 0.20999999999999963, 0.19999999999999962, 0.1899999999999996, 0.1799999999999996, 0.1699999999999996, 0.1599999999999996, 0.14999999999999958, 0.13999999999999957, 0.12999999999999956, 0.11999999999999955, 0.10999999999999954, 0.09999999999999953, 0.08999999999999952, 0.07999999999999952, 0.06999999999999951, 0.0599999999999995, 0.04999999999999949, 0.03999999999999948, 0.02999999999999947, 0.019999999999999463, 0.009999999999999454, -5.551115123125783e-16, -0.010000000000000564, -0.020000000000000573, -0.030000000000000582, -0.04000000000000059, -0.0500000000000006, -0.06000000000000061, -0.07000000000000062, -0.08000000000000063, -0.09000000000000064, -0.10000000000000064, -0.11000000000000065, -0.12000000000000066, -0.13000000000000067, -0.14000000000000068, -0.1500000000000007, -0.1600000000000007, -0.1700000000000007, -0.18000000000000071, -0.19000000000000072, -0.20000000000000073, -0.21000000000000074, -0.22000000000000075, -0.23000000000000076, -0.24000000000000077, -0.2500000000000008, -0.2600000000000008, -0.2700000000000008, -0.2800000000000008, -0.2900000000000008, -0.3000000000000008, -0.31000000000000083, -0.32000000000000084, -0.33000000000000085, -0.34000000000000086, -0.35000000000000087, -0.3600000000000009, -0.3700000000000009, -0.3800000000000009, -0.3900000000000009, -0.4000000000000009, -0.4100000000000009, -0.42000000000000093, -0.43000000000000094, -0.44000000000000095, -0.45000000000000095, -0.46000000000000096, -0.470000000000001, -0.480000000000001, -0.490000000000001, -0.500000000000001, -0.510000000000001, -0.520000000000001, -0.530000000000001, -0.540000000000001, -0.550000000000001, -0.560000000000001, -0.5700000000000011, -0.5800000000000011, -0.5900000000000011, -0.6000000000000011})
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


