#!/usr/bin/env python
# -*- coding: utf-8 -*-

#########################################################################
# 
# Copyright 2008 by Jürgen Geuter <tante@the-gay-bar.com> 
#
# thinkwhack - triggering actions on your hdaps-enabled  laptop
#
# This file is part of thinkwhack.
#
# thinkwhack is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3
# only, as published by the Free Software Foundation.
#
# thinkwhack is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License version 3 for more details
# (a copy is included in the LICENSE file that accompanied this code).
#
# You should have received a copy of the GNU General Public License
# version 3 along with thinkwhack.  If not, see
# <http://www.gnu.org/licenses/gpl-3.0.html>
# for a copy of the GPLv3 License.
########################################################################

"""actions contains all the possible actions that events can trigger"""

import os

class Action(object):
    """Abstract base Action"""

    def activate(thinkwhack, tiltevent):
        pass

class RotateAction(Action):
    """action for rotating the screen"""

    def register(self, thinkwhack):
        print ("Registering RotateAction")
        thinkwhack.register("tilt",self)
    
    def activate(self, thinkwhack, tiltevent):
        """Set the rotation of the thinkwhack (and therefore the display).
        to the given direction"""
        
        # might look counterintuitive, but when you put the 
        # laptop on the left you have to rotate the screen to the right
        rotator = {"normal": "normal",
                    "left" : "right",
                    "right": "left",
                    }
        
        #print("xrandr -o " + rotator[tiltevent.direction])
        os.system("xrandr -o " + rotator[tiltevent.direction])

#TODO: this is temporary, I'll have to do this automatically
rotator = RotateAction()
