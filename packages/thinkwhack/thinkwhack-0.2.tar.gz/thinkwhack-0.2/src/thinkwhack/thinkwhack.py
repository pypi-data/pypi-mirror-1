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

"""
The module thinkwhack.thinkwhack has all the basic functionality, the basic
event classes, the code to actually determines, which event happend, and
the code to trigger the events.
"""

import os
import re
import time
# from gettext import gettext as _
import pygtk
pygtk.require("2.0")
import gtk, gobject
# gstreamer imports
import pygst
pygst.require('0.10')
import gst

import config
import actions

## History Datastructure
class History(list):
    """History is a class derived from list that contains a maximum number of
    elements. It's basically a FIFO queue.
    """

    def __init__(self, max_size=20):
        super(History, self).__init__(self)
        self.max_size = max_size

    def pop(self):
        """Overriding the list.pop() function so we don't get the first 
        object, but the last."""
        return super(History, self).pop(0)

    def append(self, value):
        """list.append() is being overridden so we can make sure that the 
        amount of values will not exceed our limit"""
        if len(self)==self.max_size:
            # we just want a forced entry so we pop the value we 
            # wanna get rid of out of the list
            self.pop()
        super(History, self).append(value)

    def get_reversed(self):
        """Just a quick way to get the reversed List's contents without 
        modifying the list (list.reverse() works _IN PLACE_ so that's not all 
        that useful).
        """
        out = []
        for index in xrange(len(self)-1, -1, -1):
            out.append(self[index])
        return out

    def clear(self):
        """clear the history as in removing all the entries"""
        for i in xrange(len(self)):
            self.pop()

#####
# Events
#####

class BaseEvent(object):
    """Base class for all events, makes sure they can properly fire"""
    def __init__(self, whacker, direction):
        self.direction=direction
        self.whacker = whacker
        self.notify()
    
    def notify(self):
        """notify all the listeners for this event type of it's occurence"""
        for event in self.whacker.events[self.type]:
            event.activate(self.whacker, self)
        

class TiltEvent(BaseEvent):
    """TiltEvent is created when the laptop is actually being tilted to a
    side. This is useful for allowing to use xrandr to rotate the view.
    A tiltevent knows on which side the laptop was being tilted.
    direction is one of "normal", "left", "right" or "inverted". 
    Those are the xrandr names anyways so that might be useful at some point.
    The TiltEvent also sets the Thinkwhack's rotation attribute so we don't spawn needless instances.
    """
    def __init__(self, whacker, direction):
        self.whacker = whacker
        self.type = "tilt"
        self.direction=direction
        print "Tilt to the ",direction
        whacker.rotation = direction
        self.notify()

class ShockEvent(BaseEvent):
    """A shockevent is created when the laptop get's a shock as in 
    getting hit from the side.
    A shockevent should know from which direction the hit came.
    direction is "left" or "right"."""        
    pass

class SwingEvent(BaseEvent):
    """A SwingEvent represents a swinging movement, which is longer than
    a shockevent. Shocks are very short "smacks" swings are more like
    lightsaber swinging ;)"""
    pass

##
# Main class
class ThinkWhack(object):
    """ThinkWhack represents the application as well as the Laptop.
    It contains the state of the Laptop as well"""
    
    # Constants
    # TILT_DIRECTIONS tell us how the laptop is lieing
    TILT_DIRECTIONS = ("normal", "left", "right", "inverted")
    
    # setup and initialisation
    def __init__(self):
        # initial setup
        self.setup()

        #setting up the systray
        self.statusicon = gtk.status_icon_new_from_file(
                os.path.join(self.DATAPATH, "trayicon_off.png"))
        self.statusicon.connect(
                "popup-menu", self.on_tray_context_menu_event)
    
    def setup(self):
        """Figure out the path for data files and the likes."""
        self.DATAPATH = "/usr/share/thinkwhack/"
        
        # the regex to evaluate the data we get from hdaps
        self.REGEX = re.compile('^\((-?\d+),(-?\d+)\)$')
        
        self.config = config.get_conf()

        #history saves the amount of values we wanna look at
        self.history = History(self.config['HISTORY_LENGTH'])

        # rotation saves the state the laptop is in
        # it's normal, left, right or inverted
        # Initially it's "normal" so we assume the laptop is
        # in the normal display setting upon startup
        # if it's not the new state is picked up rather quick 
        # so we don't do any detection here
        self.rotation = self.TILT_DIRECTIONS[0] 

        # we start not running
        self.running = False

        #setup the event registry
        self.events = {'tilt' : [],
                'shock' : [],
                'swing' : [],
                }
        # temporary hack to get the first action in
        actions.rotator.register(self)

    def quit(self, *args):
        """quit takes care of whatever we wanna do while quitting the
        application. It does especially save the configuration."""
        print "saving config"
        self.config.write()
        gtk.main_quit()


    def on_tray_context_menu_event(self, icon, widget, time):
        """Display the context Menu for the application"""
        # Insert menuitems
        menu = gtk.Menu()
        # start/stop button
        if self.running:        
            start_stop = gtk.ImageMenuItem(gtk.STOCK_MEDIA_STOP)
            start_stop.connect("activate", self.stop)
        else:
            start_stop = gtk.ImageMenuItem(gtk.STOCK_MEDIA_PLAY)
            start_stop.connect("activate", self.start)
        menu.append(start_stop)
        # quit the application
        quit = gtk.ImageMenuItem(gtk.STOCK_QUIT)
        quit.connect("activate", self.quit)
        menu.append(quit)
        menu.show_all()
        # display the menu
        menu.popup(None, None, gtk.status_icon_position_menu, 
                widget, time, self.statusicon)
        return True
   
    
    # reading positions
    def get_position(self):
        """Return the current position of the laptop accoring to 
        self.POSITIONFILE"""
        pos = open(self.config['POSITIONFILE']).read()
        match = self.REGEX.match(pos)
        return (int(match.groups()[0]), int(match.groups()[1]))

    def get_calibration(self):
        """Return the initial calibration"""
        cal = open(self.config['CALIBRATIONFILE']).read()
        match = self.REGEX.match(cal)
        return (int(match.groups()[0]), int(match.groups()[1]))
    
    def poll(self):
        """poll reads the hdaps system and figures out what 
        to do with the results""" 
        
        # write the "now" to the history
        x, y = self.get_position()
        self.history.append((x, y))

        # call the detection algorithm that can decide what's going on
        self.process()
        
        # if we return "False" the repeated execution stops
        return self.running
  
    def process(self):
        """process is the algorithm. Well actually it just applies the
        different algorithms. Looks somewhat cleaner and makes the poll()
        function smaller."""
        self.try_tilting()

    # helper functions and alorithms
    def try_tilting(self):
        """Determine whether we do consider "now" to be a tilting event.
        In case we find the current state stable and the new state is 
        not the one we had before we create a new TiltEvent
        """
        timeline = self.history.get_reversed()
        stable = False
        # For a short history we consider it unstable 
        if len(self.history) < self.config['TILTING_LOOKBACK']:
            return False
        else:
            stable = self.is_stable(
                        timeline[:self.config['TILTING_LOOKBACK']])

        # in case it's stable we now have to create a new TiltEvent
        if stable:
            # get the calibration
            # Right now we just use the x coordinate
            calx,caly = self.get_calibration()
            x,y = timeline[0]

            if (calx - self.config['TILTING_SENSITIVITY']) > x:
                if not self.rotation == self.TILT_DIRECTIONS[1]:
                    print "Setting rotation to right"
                    # spawn the event()
                    TiltEvent(self, self.TILT_DIRECTIONS[1])
            elif (calx + self.config['TILTING_SENSITIVITY']) < x:
                if not self.rotation == self.TILT_DIRECTIONS[2]:
                    print "Setting rotation to left"
                    TiltEvent(self, self.TILT_DIRECTIONS[2])
            else:
                if not self.rotation == self.TILT_DIRECTIONS[0]:
                    print "Setting rotation to normal"
                    TiltEvent(self, self.TILT_DIRECTIONS[0])
        
        # if nothing has found it to be tilty now, it's just not 
        return False

    def is_stable(self, slice):
        """returns whether we consider a givenm History slice to be stable as
        in "having come to rest". When we turn the Laptop around we want to
        turn the display around accordingly but we want to make sure that 
        the state is stable first.
        We calculate the diff based on each state and it's predecessor.
        """
        diff = 0
        for i in xrange(len(slice)-1):
            diff += abs(abs(slice[i][0])-abs(slice[i+1][0]))
        if diff < self.config['TILTING_THRESHOLD']:
            return True
        else:
            return False
    

    # actions
    def register(self, type, action):
        """register an action to the appropriate events"""
        self.events[type].append(action)


    # some helping wrappers to allow scripts to trigger stuff
    def play_sound(self, uri):
        "Play a given sound. Uses gstreamer for format support. "
        player = gst.element_factory_make("playbin", "player")
        print 'Playing:', uri
        player.set_property('uri', uri)
        player.set_state(gst.STATE_PLAYING)


    def set_rotation(self, x, y):
        """Set the rotation of the thinkpad (and therefore the display).
        x and y are the stable coordinates of the new state"""
        # Right now we just use the x coordinate
        calx,caly = self.get_calibration()
        
        # might look counterintuitive, but when you put the 
        # laptop on the left you have to rotate the screen to the right
        if (calx-self.config['TILTING_SENSITIVITY']) > x:
            if not self.rotation == self.TILT_DIRECTIONS[1]:
                print "Setting rotation to right"
                self.rotation = self.TILT_DIRECTIONS[1]
                os.system("xrandr -o right")
        elif (calx+self.config['TILTING_SENSITIVITY']) < x:
            if not self.rotation == self.TILT_DIRECTIONS[2]:
                print "Setting rotation to left"
                self.rotation = self.TILT_DIRECTIONS[2]
                os.system("xrandr -o left")
        else:
            if not self.rotation == self.TILT_DIRECTIONS[0]:
                print "Setting rotation to normal"
                self.rotation = self.TILT_DIRECTIONS[0]
                os.system("xrandr -o normal")

    
    # thread management
    def start(self, *args):
        """start() makes the poll() thread run"""
        self.running = True
        gobject.timeout_add(self.config['INTERVAL'], self.poll)
        self.statusicon.set_from_file(
                os.path.join(self.DATAPATH, "trayicon_on.png"))
        print ("Start polling")

    def stop(self, *args):
        """stop() makes the polling stop. It also clears the history."""
        self.running = False
        time.sleep(self.config['INTERVAL']/1000.0)
        self.history.clear()
        self.statusicon.set_from_file(
                os.path.join(self.DATAPATH, "trayicon_off.png"))
        print ("Stop polling")

