#!/usr/bin/env python
# -*- coding: utf-8 -*-
# encoding: utf-8

"""An example for a fungus scene definition. """

#### Imports ####

from os import path
from pyglet.window import key
# TODO: Remove the need to import images via pyglet - use the core object we pass to the scene. 

from fungus_scene import BaseScene
from fungus_core import __copyright__

# for timing the scene we need the current unix time
from time import time

# For the battle we need random choice
from random import random, choice

# Also listdir to see the files in the audio dir
from os import listdir
from os.path import isfile, join, dirname

#### An example audio scene ####

### Things needed for the scene ###

## An audio file ##
sword_file = "sword.wav"

AUDIO_BASE_PATH = join(dirname(__file__), "audio")

### The Scene itself. 

class Scene(BaseScene): 
    """A dummy scene - mostly just the Scene API."""
    def __init__(self, core, *args, **kwds): 
        """Initialize the scene with a core object for basic functions."""
	
        ## Get the necessary attributes for any scene. 
        # This gets the 'visible', 'colliding' and 'overlay' lists 
        # as well as the scene switch 'switch_to_scene' 
        # which can be assigned a scene to switch to. 
        super(Scene, self).__init__(core, *args, **kwds)
	
	#: A list of players which can play
	self.players = []
	#: Player for the background music
	self.bg = self.core.load_player(sword_file, loop=True)
	#: Current state of the scene
	self.state = {"scene": None}
	#: The time when we started the scene
	self.start_time = time()

    def update(self): 
        """Update the stats of all scene objects. 

Don't blit them, though. That's done by the Game itself.

To show something, add it to the self.visible list. 
To add a collider, add it to the self.colliding list. 
To add an overlay sprite, add it to the self.overlay list. 
"""
	
	###Check all players if they finished and if they should loop. If they shouldn't loop, they get deleted.
	self.bg.dispatch_events()
	for player in self.players[:]: 
		player.dispatch_events()
		if not player.playing: 
			self.players.remove(player)
	
	# Start the menu in the beginning
	if self.state["scene"] is None: 
	    self.start_menu()
	
	# After 10s we switch to the intro
	if self.state["scene"] == "menu" and time() - self.start_time >= 5: 
	    if self.bg.volume > 0.0: 
		self.bg.volume -= 0.001
	    else: 
		self.start_intro()
	
	if time() - self.start_time > 10: 
	    self.core.win.has_exit = True
	    
    
    def start_menu(self): 
	"""Start the menu"""
	print "start menu"
	self.state["scene"] = "menu"
	self.bg.play()
    
    def start_intro(self): 
	"""Start the intro playback."""
	print "start intro"
	self.state["scene"] = "intro"
	self.intro_player = self.core.load_player(sword_file)
	self.bg.pause()
	self.intro_player.play()
	self.players.append(self.intro_player)
	
    
    def on_key_press(self, symbol, modifiers): 
        """Forwarded keyboard input."""
        # Use the escape key as a means to exit the game. 
        if symbol == key.ESCAPE: 
            self.core.win.has_exit = True
