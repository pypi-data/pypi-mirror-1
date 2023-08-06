#!/usr/bin/env python
# -*- coding: utf-8 -*-
# encoding: utf-8

"""An example for a fungus scene definition. 

Ideas: 
- Keyboard control via a dict similar to the command dict in Mercurial: Keyboard symbols or combinations (as tuple) as keys and methods of the scene as values. Convenience functions which add a whole set of actor control keys. This allows for dynamic key rebinding. 

"""

#### Imports ####

from fungus_core import Sprite
from pyglet.window import key

#### API definitions ####

### A "Scene method not implemented" Exception class. 

class MethodNotImplemented(Exception):
    """A warning to display if any necessary scripting function isn't implemented."""
    def __init__(self, func, implementation = None):
        self.func = func
        self.implementation = implementation

    def __str__(self):
        if self.implementation is None:
            return "The method " + str(self.func) + " must be implemented."
        else:
            return "The method " + str(self.func) + " must be implemented." + "\nThe simplest way is to just add the following lines to your class:" + self.implementation

### A base Scene class to inherit from (API definition)

class BaseScene(object): 
    """A dummy scene - mostly just the Scene API."""
    def __init__(self, core): 
        """Initialize the scene with a core object for basic functions."""
	
        ## Necessary attributes for any scene. 
        #: The core provides basic functions. It gets passed to every scene as first argument. 
        self.core = core
        #: Visible sprites. 
        self.visible = []
        #: Colliding sprites - this seperation allows for invisible colliders. 
        self.colliding = []
        #: Overlay sprites. They are above all other sprites (included for convenience, since most games need an overlay of sorts)
        self.overlay = []
        #: A scene to switch to on the next screen update. 
        self.switch_to_scene = False
        
    def update(self): 
        """Update the stats of all scene objects. """
        raise MethodNotImplemented(self.update, implementation="""    def update(self): 
        pass""")
    
    def on_key_press(self, symbol, modifiers): 
        """Forwarded keyboard input."""
        # Use the escape key as a means to exit the game. 
        if symbol == key.ESCAPE: 
            self.core.win.has_exit = True
        else: 
            pass
    
    def on_key_release(self, symbol, modifiers): 
        """Forwarded keyboard input."""
        pass
    
    def on_mouse_press(self, x, y, buttons, modifiers): 
        """Forwarded keyboard input."""
        pass
    
    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers): 
        """Forwarded keyboard input."""
        pass
    
    def on_mouse_release(self, x, y, buttons, modifiers): 
        """Forwarded keyboard input."""
        pass


#### An example scene ####

### Things needed for the scene

IMAGE_TANK = "tank.png"

### The Scene itself. 

class DummyScene(BaseScene): 
    """A dummy scene - mostly just the Scene API."""
    def __init__(self, core, *args, **kwds): 
        """Initialize the scene with a core object for basic functions."""
        
        ## Get the necessary attributes for any scene. 
        # This gets the 'visible', 'colliding' and 'overlay' lists 
        # as well as the scene switch 'switch_to_scene' 
        # which can be assigned a scene to switch to. 
        super(DummyScene, self).__init__(core, *args, **kwds)
        
        ## Tests - not necessary for every scene. 
        # Add a tank to the visible items. 	
        self.tank = self.core.sprite(IMAGE_TANK, x=212, y=208,
                                     update_func=self.tank_update)

        self.visible.append(self.tank)

    def tank_update(self, x, y): 
        """Update the tank position."""
        # Move the tank down. 
        y -=1
        # If we leave the screen, come back from the other side. 
        if y < -68:
            y = 544
        return x, y

    def update(self): 
        """Update the stats of all scene objects. 

Don't blit them, though. That's done by the Game itself.

To show something, add it to the self.visible list. 
To add a collider, add it to the self.colliding list. 
To add an overlay sprite, add it to the self.overlay list. 
"""
        self.tank.update()

