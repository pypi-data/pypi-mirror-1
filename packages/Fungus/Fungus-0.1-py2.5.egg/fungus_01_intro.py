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

#### An example scene ####

### Things needed for the scene ###

## A Level ##

# We want to display a level: That's simply a list of tiles. 
# For convenient level creation we show it as a list of letters. 
# This is for still level parts. 

# Levels currently always get shown from the top left corner. If you want 
# scrolling levels, add additional parts at the right or the bottom of the 
# level. 

# TODO: Add an option "top left corner" or similar, which signifies the level 
# position. 

# To make this cleaner and the game look nicer, this init of objects makes 
# (obj, objRect) tile tuples

o = 'floor1.png' # clear
t = 'tile2.png' # tree
g = 'tile3.png' # ground
r = 'tile4.png' # road

level = [
[o, o, o, o, o, o, r, r, r, o, o, o, o, o, o, o, o], 
[o, o, o, t, o, o, r, r, r, o, o, t, o, o, o, o, o], 
[o, o, o, o, o, o, r, r, r, o, o, t, o, o, o, o, o], 
[o, o, g, o, o, o, r, r, r, t, o, o, o, o, o, o, o], 
[o, o, o, o, o, o, r, r, r, o, o, o, o, o, o, o, o], 
[o, o, o, o, o, o, r, r, r, o, o, o, o, o, o, o, o], 
[o, o, o, o, o, o, r, r, r, o, g, o, o, o, o, o, o], 
[o, o, o, o, o, g, r, r, r, o, o, o, o, o, o, o, o], 
[o, o, o, o, o, o, r, r, r, o, o, o, o, o, o, o, o], 
[o, o, o, o, o, o, r, r, r, o, o, o, o, o, o, o, o], 
[o, o, o, o, o, o, r, r, r, o, o, o, o, o, o, o, o], 
[o, o, o, o, o, o, r, r, r, o, o, o, o, o, o, o, o], 
[o, o, o, o, o, o, r, r, r, o, o, o, o, o, o, o, o], 
[o, o, o, o, o, o, r, r, r, o, o, o, o, o, o, o, o], 
[o, o, o, o, o, o, r, r, r, o, o, o, o, o, o, o, o], 
[o, o, o, o, o, o, r, r, r, o, o, o, o, o, o, o, o], 
[o, o, o, o, o, o, r, r, r, o, o, o, o, o, o, o, o], 
[o, o, o, o, o, o, r, r, r, o, o, o, o, o, o, o, o], 
[o, o, o, o, o, o, r, r, r, o, o, o, o, o, o, o, o], 
[o, o, o, o, o, o, r, r, r, o, o, o, o, o, o, o, o], 
[o, o, o, o, o, o, r, r, r, o, o, o, o, o, o, o, o], 
]


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

        # Add an actor, who should be controllable with the keyboard.
        self.actor = self.core.sprite("tank5.png", x=217, y=183)
        
        # Also add a speach box
        self.text_box = self.core.sprite("box2.png", y=-2)
        # and a text to show in that. 
        self.text = self.core.load_text('Just get us back to the bunker before sunset.', x=14, y=48)

        # Load the level
        self.level = self.load_level(level)
        # And add the level sprites to the visible list. 
        for y in self.level: 
            for x in y: 
                self.visible.append(x)
        
        # Finally add the actor, so it's shown on top. 
        self.visible.append(self.actor)
        
        # And add the speech box and the text to the overlay
        self.overlay.append(self.text_box)
        self.overlay.append(self.text)
        
    def actor_update(self, x, y): 
        """Update the actor position.
        
        To change the movement pattern, just use self.actor.update_func=new_fun
        """
        # Move the tank down. 
        y -=1
        # If we leave the screen, come back from the other side. 
        if y <= -32:
            y = 511
        return x, y

    def load_level(self, level): 
        """Load a level with image names and return it as level with image objects."""
        new_level = []
        for y in range(len(level)): 
            new_level.append([])
            for x in range(len(level[y])): 
                # Load a sprite with the coordinates from the level. 
                sprite = self.core.sprite(level[y][x], x=32*x, y=32*y)
                new_level[y].append(sprite)
        return new_level

    def update(self): 
        """Update the stats of all scene objects. 

Don't blit them, though. That's done by the Game itself.

To show something, add it to the self.visible list. 
To add a collider, add it to the self.colliding list. 
To add an overlay sprite, add it to the self.overlay list. 
"""
        # Update the actor
        self.actor.update()
        # move all level tiles
        for x in self.level: 
            for y in x: 
                # Move the tile
                y.y +=1
                # If we leave the screen, come back from the other side. 
                if y.y >= 512:
                    y.y = -31
        
    
    def on_key_press(self, symbol, modifiers): 
        """Forwarded keyboard input."""
        # Use the escape key as a means to exit the game. 
        if symbol == key.ESCAPE: 
            self.core.win.has_exit = True
        # TODO: Remove this debug output
        else: 
            print modifiers, symbol
        #: Basic actor movement with the keyboard
        self.core.keyboard_movement_key_press(self.actor, symbol, modifiers)
            
    def on_key_release(self, symbol, modifiers): 
        """Forwarded keyboard input."""
        #: Basic actor movement with the keyboard
        self.core.keyboard_movement_key_release(self.actor, symbol, modifiers)
