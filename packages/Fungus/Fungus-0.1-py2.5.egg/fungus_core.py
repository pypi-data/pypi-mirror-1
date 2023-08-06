#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Fungus - Live and die in a world of mold

core functions: 
- scrolling text.

Ideas: 
- maybe replace .blit() everywhere with .draw()
- core: Offer a lightweight sprite and an actor sprite inszead of only the normal sprite to avoid unecessary overhead. The actor sprite contains the functions for keyboard control, the lightweight sprite only has basic movement (dx, dy, x, y). 
"""

__copyright__ = """ 
  Fungus - Live and die in a world of mold
----------------------------------------------------------------- 
© 2008 - 2009 Copyright by Arne Babenhauserheide

  This program is free software; you can redistribute it and/or modify
  it under the terms of the GNU General Public License as published by
  the Free Software Foundation; either version 2 of the License, or
  (at your option) any later version.

  This program is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU General Public License for more details.

  You should have received a copy of the GNU General Public License
  along with this program; if not, write to the Free Software
  Foundation, Inc., 51 Franklin St, Fifth Floor, Boston,
  MA 02110-1301 USA

""" 

from pyglet import image
from os.path import dirname, join
from pyglet.window import key
#from pyglet import clock
from pyglet import font
# Media playing stuff (video and audio)
from pyglet.media import Player
from pyglet.media import load, StaticSource

### The Core Object ###

"""The Core object offers several convenience functions to speed up game development."""

## Audio player which knows looping
class Player(Player): 
    """A player which knows if it should loop."""
    def __init__(self, loop=False, *args, **kwds):
	super(Player, self).__init__(*args, **kwds)
	self.loop = loop
	if self.loop: 
	    self.eos_action = self.EOS_LOOP
	else: 
	    self.eos_action = self.EOS_PAUSE


## Sprites ##

class Sprite(object):
    def __init__(self, image_path, x = 212, y = 208, update_func=None):
        """Create a simple sprite. 

@param image_path: the path to the image, relative to the graphics folder. 
@param x: horizontal position. 
@param y: vertical position. 
@param update_func: A function to update the Sprite position. If defined, it has to take x, y and return new x, y. 
"""
        self.x = x
        self.y = y
        #: Continuous movement into x direction for movement when holding down a key
        self.d_left = 0
	#: Continuous movement into x direction for movement when holding down a key
	self.d_right = 0
        #: Continuous movement into y direction for movement when holding down a key
        self.d_up = 0
	#: Continuous movement into y direction for movement when holding down a key
	self.d_down = 0
	#: Delayed continuous movement into x direction, beginning only with the update cycle after the next.
	self.dd_left = 0
	#: Delayed continuous movement into x direction, beginning only with the update cycle after the next.
	self.dd_right = 0
	#: Delayed continuous movement into y direction, beginning only with the update cycle after the next.
	self.dd_up = 0
	#: Delayed continuous movement into y direction, beginning only with the update cycle after the next.
	self.dd_down = 0
        self.image = image.load(image_path)
        self.update_func = update_func
        self.width = self.image.width
        self.height = self.image.height
        
    def blit(self): 
        """Draw the sprite at its coordinates."""
        self.image.blit(self.x, self.y)

    def update(self): 
        """Update the sprite."""
        # Basic continuous movement
        if self.d_left: 
            self.x -= self.d_left
        if self.d_right: 
            self.x += self.d_right
        if self.d_up: 
            self.y += self.d_up
        if self.d_down: 
            self.y -= self.d_down
	# Prepare delayed continuous movement
	if self.dd_right: 
            self.d_right += self.dd_right
	    self.dd_right = 0
	if self.dd_left: 
            self.d_left += self.dd_left
	    self.dd_left = 0
        if self.dd_up: 
            self.d_up += self.dd_up
	    self.dd_up = 0
        if self.dd_down: 
            self.d_down += self.dd_down
	    self.dd_down = 0
	# The update function. 
        if self.update_func is not None: 
            self.x, self.y = self.update_func(self.x, self.y)
        else: 
            pass


class Core(object): 
    """Basic functions for scenes.

Basics: 
- The core provides a core object which gets passed to every new scene. This core 
object gives the scenes basic functions like moving, collision detection and 
similar (to avoid having to load them for every new scene). 
- Also it holds some basic configuration settings needed by the scenes (like the 
graphics path). 

The core can contain nothing which needs access to the game window or event loop. 

"""
    def __init__(self, graphics_dir = "graphics", audio_dir = "audio", *args, **kwds):
        # And define the folder to use for graphics. 
        self.image_base_folder = join(dirname(__file__), graphics_dir)
	self.audio_base_folder = join(dirname(__file__), audio_dir)
        # TODO: Write core. 

    def sprite(self, image_path, x = 0, y = 0, update_func=None): 
        """Create a sprite which can blit itself and has x and y coordinates."""
        sprite = Sprite(join(self.image_base_folder, image_path), x=x, y=y, update_func=update_func)
        return sprite
	
    def load_image(self, img_path):
        """Create an image object which can be blitted.

        This is just a wrapper for a pyglet function.
        """
        return image.load(join(self.image_base_folder, img_path))

    def load_text(self, text, font_type = "Arial", font_size=14, x=10, y=75): 
        """Create a text object which can be blitted.

        This is just a wrapper for a pyglet function.
        """
        label = font.Text(font.load(font_type, font_size),text, x, y)
        # Give the label the same ability to blit itself as any other sprite.
        label.blit = label.draw
        return label
        
    def preload_scene(self, scene_class, scene_object): 
        """Preload a scene in a seperate thread to avoid interrupting the game flow, since loading a scene can take longer than one frame. 
        
        @return: An instance of the scene_class.
        """
        raise NotImplementedException("TODO")
    
    def load_player(self, source_file=None, loop=False, streaming = False): 
	"""@return: a player which can play audio files."""
	player = Player(loop=loop)
	if source_file is not None: 
	    source = self.load_media_source(source_file, streaming=streaming)
	    player.queue(source)
	return player
    
    def load_media_source(self, source_file, streaming = False): 
	"""@return: A static pyglet source which can be attached to an arbitaary number of players. 
	
	It is decoded on creation and stored in memory.."""
	source = load(join(self.audio_base_folder, source_file))
	if streaming: 
	    return source
	return StaticSource(source)

    def keyboard_movement_key_press(self, actor, symbol, modifiers): 
        """Basic keyboard movement.


        Movement from keypad. 
        We use direct change as well as continuous movement to make the actor react quickly. 
        Note: ddx and ddy allow for delayed continuous movement. The first step is always done."""
        if symbol == key.LEFT:
            actor.x -= 10 
            actor.dd_left = 10
        elif symbol == key.RIGHT: 
            actor.x += 10
            actor.dd_right = 10
        elif symbol == key.DOWN: 
            actor.y -= 10
            actor.dd_down = 10
        elif symbol == key.UP: 
            actor.y += 10
            actor.dd_up = 10

    def keyboard_movement_key_release(self, actor, symbol, modifiers): 
        """Basic keyboard movement.

	Note: ddx = ddy = 0 stop delayed continuous movement. 
	
	As safety: If we move in one direction and the key in that direction is released, the movement into that direction always stops. 
        """
        if symbol == key.LEFT: 
            actor.dd_left = 0
	    actor.d_left = 0
        elif symbol == key.RIGHT: 
            actor.dd_right = 0
	    actor.d_right = 0
        elif symbol == key.DOWN: 
	    actor.dd_down = 0
	    actor.d_down = 0
        elif symbol == key.UP: 
            actor.dd_up = 0
	    actor.d_up = 0
          
    def point_is_inside(self, area, x, y): 
        """Check if some point is inside an area. 
        
        @param area: Something which has x, y, width and height.
        """
        if x > area.x and x < area.x + area.width and y > area.y and y < area.y + area.height: 
            return True
        else: 
            return False


#### Self-Test ####

if __name__ == "__main__": 
    pass



