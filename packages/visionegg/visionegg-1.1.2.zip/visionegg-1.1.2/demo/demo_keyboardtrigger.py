#!/usr/bin/env python
"""Use the keyboard to trigger the Vision Egg."""

# Author(s): Hubertus Becker <hubertus.becker@uni-tuebingen.de>
# Copyright: (C) 2005 by Hertie Institute for Clinical Brain Research,
#            Department of Cognitive Neurology, University of Tuebingen
# URL:       http://www.hubertus-becker.de/resources/visionegg/
# $Revision: 1529 $  $Date: 2009-01-30 10:18:31 -0800 (Fri, 30 Jan 2009) $

import VisionEgg
VisionEgg.start_default_logging(); VisionEgg.watch_exceptions()

from VisionEgg.Core import *
from VisionEgg.FlowControl import Presentation, ConstantController
from VisionEgg.Gratings import *
import VisionEgg.Daq
from VisionEgg.DaqKeyboard import *
import pygame

# Normal stuff (from grating demo):
screen = get_default_screen()
stimulus = SinGrating2D(
    on               = 0, # turn grating is off when not in go loop
    position         = ( screen.size[0]/2.0, screen.size[1]/2.0 ),
    anchor           = 'center',
    size             = ( 300.0 , 300.0 ),
    spatial_freq     = 10.0 / screen.size[0],
    temporal_freq_hz = 5.0,
    orientation      = 45.0
)

viewport = Viewport( screen=screen, stimuli=[stimulus] )
p = Presentation(
    go_duration=(5.0,'seconds'),
    trigger_go_if_armed=0, # wait for trigger
    viewports=[viewport]
)

# Stimulus on controller
stimulus_on_controller = ConstantController(during_go_value=1,between_go_value=0)

# Create a trigger input controller
trigger_in_controller = KeyboardTriggerInController() # Default is key '1'
#trigger_in_controller = KeyboardTriggerInController(pygame.locals.K_2) # Use '2'

# Add the trigger output controller to the presentation's list of controllers
p.add_controller(stimulus,'on',stimulus_on_controller)
p.add_controller(p,'trigger_go_if_armed',trigger_in_controller)

# Go!
p.go()
p.go()
p.go()
