
 

-- Clear the front panel display then prompt for input parameters if missing. 

display.clear()   

startv = 0.05

stopv = 0.7

stime = 0.01

points = 10000

-- Update display with test info. 

display.settext("SweepVLinMeasureI")  -- Line 1 (20 characters max) 

-- choose the channel
smu = smua

-- Configure source and measure settings. 

smu.source.output = smu.OUTPUT_OFF 

smu.source.func = smu.OUTPUT_DCVOLTS 

smu.source.levelv = 0 

smu.source.rangev = math.max(math.abs(startv), math.abs(stopv)) 

smu.measure.autozero = smu.AUTOZERO_OFF 

-- Setup a buffer to store the result(s) in and start testing. 

smu.nvbuffer1.clear() 

smu.nvbuffer1.appendmode = 0 

smu.nvbuffer1.collecttimestamps = 1 

smu.nvbuffer1.collectsourcevalues = 1 

-- smua.nvbuffer1.fillmode = FILL_WINDOW

smu.nvbuffer1.fillcount = 0

smu.nvbuffer1.timestampresolution = 0.001 


-- Reset trigger model 

smu.trigger.arm.stimulus = 0 

smu.trigger.source.stimulus = 0 

smu.trigger.measure.stimulus = 0 

smu.trigger.endpulse.stimulus = 0 

smu.trigger.arm.count = 1 

-- Configure the source action 

smu.trigger.source.listv({0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.7, 0.7, 0.7, 0.7, 0.7, 0.7, 0.7, 0.7, 0.7, 0.7, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05})

smu.trigger.source.action = smu.ENABLE 

smu.trigger.endpulse.action = smu.SOURCE_HOLD 

-- Configure the measure action 

smu.trigger.measure.i(smu.nvbuffer1) 

smu.trigger.measure.action = smu.ENABLE 

smu.measure.nplc = 0.01


-- Configure the delay 

if (stime > 0) then 

        trigger.timer[1].reset() 

        trigger.timer[1].delay = stime 
        
        trigger.timer[1].passthrough = false

        smu.trigger.measure.stimulus = trigger.timer[1].EVENT_ID

        trigger.timer[1].stimulus = smu.trigger.SOURCE_COMPLETE_EVENT_ID 
end

-- Configure the sweep count 

smu.trigger.count = points 

-- Run the sweep and then turn the output off. 

   -- turn the smub for gate voltage at 0
smub.source.func = smub.OUTPUT_DCVOLTS
smub.source.levelv = 0
smub.source.output = smub.OUTPUT_ON 
-- turn on the smua for signal voltage
smu.source.output = smu.OUTPUT_ON 

smu.trigger.initiate() 

waitcomplete() 

smu.source.output = smu.OUTPUT_OFF 
smub.source.output = smub.OUTPUT_OFF
-- Update the front panel display and restore modified settings. 

display.setcursor(2,1)              

display.settext("Test complete.")     -- Line 2 (32 characters max) 

delay(2) 

display.clear() 

