-- reference: 2600BS-901-01F_2600B_Reference_Aug2021.pdf - page 4-21
-- Reset the SourceMeter instrument to default conditions.
reset()

local pulse_v, bias_v
local range_v, limit_i
local pulse_period, pulse_width, deta_t
local number_pulses

display.clear() 
display.settext("InterchannelPulseVTrain")

-- [V]
pulse_vd = 0.2 
pulse_vg = 0.4
bias_v = 0

if math.abs(pulse_vg) > math.abs(pulse_vd) then 

    range_v = pulse_vg 

else 

    range_v = pulse_vd 

end 

limit_i = 1

-- [s]
pulse_period = 0.4
pulse_width = 0.02
deta_t = 0.05

--- passthrough = true -> desired number of pulses -1 
number_pulses= 9

-- configure output offmode 
smua.source.offmode = smua.OUTPUT_ZERO
smua.source.offfunc = smua.OUTPUT_DCVOLTS

smub.source.offmode = smub.OUTPUT_ZERO
smub.source.offfunc = smub.OUTPUT_DCVOLTS
-- Generate a 10-point pulse train with the following characteristics:
-- * Bias (Idle) Level = 0 V
-- * Pulse Level = 200 mV
-- * Pulse Width = 20 ms
-- * Pulse Period = 100 ms
-- Configure the source function.
smua.source.func = smua.OUTPUT_DCVOLTS
smub.source.func = smub.OUTPUT_DCVOLTS
-- Set the voltage source range and the bias source level and limit.
smua.source.rangev = range_v
smua.source.levelv = bias_v
smua.source.limiti = limit_i

smub.source.rangev = range_v
smub.source.levelv = bias_v
smub.source.limiti = limit_i
-- Use trigger timer 1 to control the period and trigger timer 2 to control the 
-- pulse width. Alias the timers for convenience and clarity.
period_timer = trigger.timer[1]
pulsewidth_timer = trigger.timer[2]

delay_timer = trigger.timer[3]
period_timer_b = trigger.timer[5]
pulsewidth_timer_b = trigger.timer[4]

-- SMUA, period
-- Configure the period timer to output 10 total trigger events.
period_timer.delay = pulse_period
-- The effective count is 10 because the passthrough setting is true.
period_timer.count = number_pulses
-- Configure the timer to immediately output a trigger event when it is started.
period_timer.passthrough = true
-- Start the timer when the SMU moves from the ARM layer to the TRIGGER layer.
period_timer.stimulus = smua.trigger.ARMED_EVENT_ID

-- Delta_t = T_pre- T_pulse
-- Configure the period timer to output 1 total trigger events.
delay_timer.delay = deta_t
-- The effective count is 1 because the passthrough setting is false.
delay_timer.count = 1
-- Configure the timer to immediately output a trigger event when it is started.
delay_timer.passthrough = false
-- Start the timer when the SMU moves from the ARM layer to the TRIGGER layer.
delay_timer.stimulus = smua.trigger.ARMED_EVENT_ID

-- SMUB, period
-- Configure the period timer to output 10 total trigger events.
period_timer_b.delay = pulse_period
-- The effective count is 10 because the passthrough setting is true.
period_timer_b.count = number_pulses
-- Configure the timer to immediately output a trigger event when it is started.
period_timer_b.passthrough = true
-- Start the timer with the delay_timer output trigger event.
period_timer_b.stimulus = delay_timer.EVENT_ID

--SMUA, pulse 
-- Configure the pulse width timer to output one trigger event for each period.
pulsewidth_timer.delay = pulse_width
pulsewidth_timer.count = 1
-- Do not immediately output a trigger event when pulse width timer is started.
pulsewidth_timer.passthrough = false
-- Start the pulse width timer with the period timer output trigger event.
pulsewidth_timer.stimulus = period_timer.EVENT_ID

--SMUB, pulse 
-- Configure the pulse width timer to output one trigger event for each period.
pulsewidth_timer_b.delay = pulse_width
pulsewidth_timer_b.count = 1
-- Do not immediately output a trigger event when pulse width timer is started.
pulsewidth_timer_b.passthrough = false
-- Start the pulse width timer with the period timer output trigger event.
pulsewidth_timer_b.stimulus = period_timer_b.EVENT_ID

-- Configure the trigger model to execute a 10-point fixed-level voltage pulse 
-- train. No measurements are made.
smua.trigger.source.listv({pulse_vd})
smua.trigger.source.action = smua.ENABLE
smua.trigger.measure.action = smua.DISABLE

smub.trigger.source.listv({pulse_vg})
smub.trigger.source.action = smub.ENABLE
smub.trigger.measure.action = smub.DISABLE

-- Set the trigger source limit, which can be different than the bias limit.
-- This is an important setting for pulsing in the extended operating area.
smua.trigger.source.limiti = limit_i
smua.measure.rangei = limit_i

smub.trigger.source.limiti = limit_i
smub.measure.rangei = limit_i

-- Trigger SMU source action with the period timer event.
smua.trigger.source.stimulus = period_timer.EVENT_ID

smub.trigger.source.stimulus = period_timer_b.EVENT_ID

-- Configure the endpulse action to achieve a pulse.
smua.trigger.endpulse.action = smua.SOURCE_IDLE

smub.trigger.endpulse.action = smub.SOURCE_IDLE

-- Trigger the SMU end pulse action with a pulse width timer event.
smua.trigger.endpulse.stimulus = pulsewidth_timer.EVENT_ID

smub.trigger.endpulse.stimulus = pulsewidth_timer_b.EVENT_ID

-- Set the trigger model count to generate one 10-point pulse train.
smua.trigger.arm.count = 1
smua.trigger.count = number_pulses + 1

smub.trigger.arm.count = 1
smub.trigger.count = number_pulses + 1

-- Turn on the SMU output and initiate the trigger model to output the pulse train.
smua.source.output = smua.OUTPUT_ON

smub.source.output = smub.OUTPUT_ON

smua.trigger.initiate()
smub.trigger.initiate()
 
-- Wait for the sweep to complete.
waitcomplete()
-- Turn off SMU output.
smua.source.output = smua.OUTPUT_OFF
smub.source.output = smub.OUTPUT_OFF

display.setcursor(2,1) 
display.settext("Complete.")
delay(2)
display.clear()
-- define output off state: 2600BS-901-01F_2600B_Reference_Aug2021.pdf - smuX.source.offmode
-- tutorial: https://www.youtube.com/watch?v=Yvyvlwsb4KQ