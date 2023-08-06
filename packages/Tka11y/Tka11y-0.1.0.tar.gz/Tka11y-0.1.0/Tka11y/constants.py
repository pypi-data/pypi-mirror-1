'''Constants for Accessibility-aware Tkinter.
   Some of these constants may be modified by the user.
'''
# Fetch version information written by setup.
from version import *

# Debug level.
Debug = 0

# Location of the atk-bridge module. If this must be changed, do so before
# creating the first widget.
AtkBridgePath = '/usr/lib/gtk-2.0/modules/'

# Constants that control the frequency of calls to the ATK iterate function,
# which processes the external ATK interface. When there is no activity,
# the maximum delay of MaxAtkIterateDelay is used between calls. Immediately
# after some activity, the delay is set to zero, after which it increments
# by AtkIterateDelayStep after each call until the maximum is reached again.
# This approach gives good system performance during idle times and rapid
# response during active times. The gradual ramp to the maximum delay handles
# bursty communications traffic in the ATK external interface. Note that
# transitioning from idle to active can take as long as MaxAtkIterateDelay,
# so it should not be set too high.
MaxAtkIterateDelay = 20 # msec
AtkIterateDelayStep = 0.02 # msec
