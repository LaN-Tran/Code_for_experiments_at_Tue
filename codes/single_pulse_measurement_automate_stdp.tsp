-- reference: factory code - PulseVMeasureI
-- Temporary variables used by this function. 
reset()
local l_tonwm
local bias, level
local ton, toff
local points

    -- Clear the front panel display then prompt for input parameters if missing. 

display.clear() 

bias = 0

level = 0.8

ton = 0.02

toff = 1.5

points = 1

-- Update display with test info. 

display.settext("PulseVMeasureI")  -- Line 1 (20 characters max)  

-- by default, smua  
smu = smua

-- output off mode
smu.source.offmode = smu.OUTPUT_ZERO
smu.source.offfunc = smu.OUTPUT_DCVOLTS

-- function configuration
smu.source.output = smu.OUTPUT_OFF 

smu.source.rangev = level

smu.source.levelv = bias

smu.source.func = smu.OUTPUT_DCVOLTS 

smu.measure.autozero = smu.AUTOZERO_OFF 

smu.measure.autorangei = smu.AUTORANGE_ON

smu.measure.filter.enable = smu.FILTER_OFF

smu.measure.nplc = 0.1--1

l_tonwm = ton - (smu.measure.nplc/localnode.linefreq) - 250E-6 

-- Setup a buffer to store the result(s) in and start testing. 

smu.nvbuffer1.clear() 

smu.nvbuffer1.appendmode = 1 

smu.nvbuffer1.collecttimestamps = 1 

smu.nvbuffer1.collectsourcevalues = 1 

-- Configure triggering. 

smu.trigger.arm.stimulus = 0 

trigger.timer[1].reset() 

trigger.timer[1].delay = l_tonwm 

trigger.timer[1].count = 1 

trigger.timer[1].stimulus = smu.trigger.SOURCE_COMPLETE_EVENT_ID 

smu.trigger.measure.stimulus = trigger.timer[1].EVENT_ID 

trigger.timer[2].reset() 

trigger.timer[2].delay = ton 

trigger.timer[2].count = 1 

trigger.timer[2].stimulus = smu.trigger.SOURCE_COMPLETE_EVENT_ID 

smu.trigger.endpulse.stimulus = trigger.timer[2].EVENT_ID 

trigger.timer[3].reset() 

trigger.timer[3].delay = toff 

trigger.timer[3].count = 1 

trigger.timer[3].stimulus = smu.trigger.PULSE_COMPLETE_EVENT_ID 

smu.trigger.source.stimulus = trigger.timer[3].EVENT_ID 

smu.trigger.source.linearv(level, level, 1) 

smu.trigger.source.action = smu.ENABLE 

smu.trigger.measure.i(smu.nvbuffer1) 

smu.trigger.measure.action = smu.ENABLE 

smu.trigger.endpulse.action = smu.SOURCE_IDLE 

smu.trigger.arm.count = 1 

smu.trigger.count = points 

-- Initiate the pulses 

smu.source.output = smu.OUTPUT_ON 

smu.trigger.initiate() 

delay(toff) 

smu.trigger.source.set() 

waitcomplete() 

delay(toff) 

smu.source.output = smu.OUTPUT_OFF 

-- Update the front panel display and restore modified settings. 

display.setcursor(2,1) 

display.settext("Test complete.")  -- Line 2 (32 characters max) 

delay(2)

display.clear() 
