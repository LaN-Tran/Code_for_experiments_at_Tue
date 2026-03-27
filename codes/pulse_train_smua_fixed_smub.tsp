-- reference: 2600BS-901-01F_2600B_Reference_Aug2021.pdf - page 4-21
-- Reset the SourceMeter instrument to default conditions.
reset()

local bias_v
local range_v, limit_i
local pulse_period, pulse_width
local number_pulses

display.clear() 
display.settext("PulseV_A_FixedV_B")

-- [V]
-- smub (gate)
-- smua (drain)
smu1 = smua
smu2 = smub

pulse_vd = 2.5
fixed_vg = 2.5

pulse_v1 = pulse_vd
pulse_v2 = fixed_vg

bias_v = 0

if math.abs(pulse_v2) > math.abs(pulse_v1) then 

    range_v = pulse_v2 

else 

    range_v = pulse_v1 

end 

limit_i = 0.1

-- [s]
pulse_period = 0.1--0.5
pulse_width = 0.02--0.1

--- passthrough = true -> desired number of pulses -1 
number_pulses= 6

-- configure output offmode 
smu1.source.offmode = smu1.OUTPUT_ZERO
smu1.source.offfunc = smu1.OUTPUT_DCVOLTS

smu2.source.offmode = smu2.OUTPUT_ZERO
smu2.source.offfunc = smu2.OUTPUT_DCVOLTS
-- Generate a 10-point pulse train with the following characteristics:
-- * Bias (Idle) Level = 0 V
-- * Pulse Level = 200 mV
-- * Pulse Width = 20 ms
-- * Pulse Period = 100 ms
-- Configure the source function.
smu1.source.func = smu1.OUTPUT_DCVOLTS
smu2.source.func = smu2.OUTPUT_DCVOLTS
-- Set the voltage source range and the bias source level and limit.
smu1.source.rangev = range_v
smu1.source.levelv = bias_v
smu1.source.limiti = limit_i

smu2.source.rangev = range_v
smu2.source.levelv = bias_v
smu2.source.limiti = limit_i
-- Use trigger timer 1 to control the period and trigger timer 2 to control the 
-- pulse width. Alias the timers for convenience and clarity.
period_timer = trigger.timer[1]
pulsewidth_timer = trigger.timer[2]

-- smu1, period
-- Configure the period timer to output 10 total trigger events.
period_timer.delay = pulse_period
-- The effective count is 10 because the passthrough setting is true.
period_timer.count = number_pulses
-- Configure the timer to immediately output a trigger event when it is started.
period_timer.passthrough = true
-- Start the timer when the SMU moves from the ARM layer to the TRIGGER layer.
period_timer.stimulus = smu1.trigger.ARMED_EVENT_ID


--smu1, pulse 
-- Configure the pulse width timer to output one trigger event for each period.
pulsewidth_timer.delay = pulse_width
pulsewidth_timer.count = 1
-- Do not immediately output a trigger event when pulse width timer is started.
pulsewidth_timer.passthrough = false
-- Start the pulse width timer with the period timer output trigger event.
pulsewidth_timer.stimulus = period_timer.EVENT_ID


-- Configure the trigger model to execute a 10-point fixed-level voltage pulse 
-- train. No measurements are made.
smu1.trigger.source.listv({pulse_v1})
smu1.trigger.source.action = smu1.ENABLE
smu1.trigger.measure.action = smu1.DISABLE

-- Set the trigger source limit, which can be different than the bias limit.
-- This is an important setting for pulsing in the extended operating area.
smu1.trigger.source.limiti = limit_i
smu1.measure.rangei = limit_i

-- Trigger SMU source action with the period timer event.
smu1.trigger.source.stimulus = period_timer.EVENT_ID

-- Configure the endpulse action to achieve a pulse.
smu1.trigger.endpulse.action = smu1.SOURCE_IDLE

-- Trigger the SMU end pulse action with a pulse width timer event.
smu1.trigger.endpulse.stimulus = pulsewidth_timer.EVENT_ID

-- Set the trigger model count to generate one 10-point pulse train.
smu1.trigger.arm.count = 1
smu1.trigger.count = number_pulses + 1

-- Turn on the SMU output and initiate the trigger model to output the pulse train.
smu1.source.output = smu1.OUTPUT_ON

-- Turn on the supply for neuron
smu2.source.levelv = fixed_vg
smu2.source.output = smu2.OUTPUT_ON

-- make sure the supply voltage by smu2 is stable before pulsing
delay(5)
smu1.trigger.initiate()
 
-- Wait for the sweep to complete.
waitcomplete()
-- Turn off SMU output.
-- smu1.source.output = smu1.OUTPUT_OFF
-- smu2.source.output = smu2.OUTPUT_OFF

display.setcursor(2,1) 
display.settext("Complete.")
delay(2)
display.clear()
-- define output off state: 2600BS-901-01F_2600B_Reference_Aug2021.pdf - smuX.source.offmode
-- tutorial: https://www.youtube.com/watch?v=Yvyvlwsb4KQ