#!/usr/bin/python
# -*- coding: utf-8 -*-

"""Fungus - Live and survive in a world filled with mold.

The main script for starting Fungus games. 

Usage: 
    - python fungus_game.py
      start the default Scene. 
    - python fungus_game.py gamefile.Scene
      start with a custom Scene

Examples: 
    - python fungus_game.py fungus_01_intro.Scene
      Start the fungus Intro

For developers: 
    - Just clone the fungus project from the Mercurial repository and add your scenes inside it. 
      Distribute them along with the fungus engine. 

Mercurial repository: 
    - http://freehg.org/u/ArneBab/fungus/

To adjust the default scene, just import another one as Scene in fungus_game.py
"""

### Imports ###

# Load sleep to limit the CPU usage
from time import sleep

# Load necessary pyglet classes
from pyglet import window
from pyglet.gl import *

# load the fungus core
from fungus_core import Core

# Load a basic scene for testing. 
from fungus_scene import DummyScene as Scene


### Classes ###

class Game(object):
    """The main game class. 

Basics: 
- The Game class acts as basic game layer and provides an API which the scenes can use. 
- It starts the scenes and passes them a core object. 
- It also contains the main event loop in which it calls the update function of 
the scenes. 
- Additionally it forwards events to the scene. 

    """
    def __init__(self, name="Fungus", width=480, height=360, fullscreen=False, graphics_dir = "graphics", first_scene = Scene, *args, **kwds):
        """Initialize the game.
        
        @param first_scene: The Scene the game starts with. 
        @type first_scene: BaseScene
        """
        
        # First get a pyglet window
        if not fullscreen: 
            self.win = window.Window(width=width, height=height, fullscreen=fullscreen, caption=name)
        else: 
            self.win = window.Window(fullscreen=fullscreen, resizable=False, caption=name)
        # And activate tranparency for pngs
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        # Then load a core object with basic functionality for the scenes
        self.core = Core(graphics_dir = graphics_dir)
        # Pass the core a rference to the window, so the scenes can access it
        self.core.win = self.win

        # Now add the first scene.
        self.scene = first_scene(self.core)

    def event_loop(self):
        """Start the main event loop."""
        while not self.win.has_exit:
            # First let pyglet call the event listener functions.
            self.win.dispatch_events()
            
            # Wait a moment, so we don't take up all processing power
            sleep(0.001)
            
            # Then clear the screen, update everything and show it. 
            self.win.clear()
            self.update()
            self.win.flip()

    def update(self):
        """Update the screen. 

This means first updating the state of everything and then blitting it on the 
screen.

Also do scene switching, when the scene calls for it. 
        """
        try: 
            self.scene.update()
            for i in self.scene.visible:
                i.blit()
            for i in self.scene.overlay:
                i.blit()
        except: 
            pass
	
        # If the scene defined a scene to switch to, we replace the scene with that new scene. 
        if self.scene.switch_to_scene: 
            self.scene = self.scene.switch_to_scene

    def on_key_press(self, symbol, modifiers):
        """Forward all key events to the scene, if the scene takes them. 

        Ideas: 
            - catch some key events directly as game controls (right, left, up, down, fire, ...), so we can define a keyboard layout at the game level and have every scene take that automatically. 
        """
        try: 
            self.scene.on_key_press(symbol, modifiers)
        except: 
            pass


### Command Line UI ###

def _help():
    return "\n".join(__doc__.splitlines()[2:])


### Self-Test ###

if __name__ == "__main__": 
    from sys import argv
    # Firstoff: If the user wants help, then help out :) 
    if "--help" in argv or "-h" in argv: 
        print _help()
        exit()
    
    # Initialize the game
    if "--fullscreen" in argv: 
	argv.remove("--fullscreen")
	game = Game(fullscreen = True)
    else: 
	game = Game()

    # Get the first scene via the commandline. 
    # Remove this, if your players should be able to skip scenes. 
    
    if len(argv) > 1: 
        mod = eval("__import__('" + argv[1].split(".")[0] + "')")
        game.scene = mod.__dict__[argv[1].split(".")[1]](game.core)
    
    # Activate supported events
    # key press
    @game.win.event
    def on_key_press(symbol, modifiers): 
        game.on_key_press(symbol, modifiers)
    
    # key release
    @game.win.event
    def on_key_release(symbol, modifiers): 
        game.scene.on_key_release(symbol, modifiers)
    
    # mouse press
    @game.win.event
    def on_mouse_press(x, y, buttons, modifiers): 
        game.scene.on_mouse_press(x, y, buttons, modifiers)
    
    # mouse drag 
    @game.win.event
    def on_mouse_drag(x, y, dx, dy, buttons, modifiers): 
        game.scene.on_mouse_drag(x, y, dx, dy, buttons, modifiers)
    
    # mouse press
    @game.win.event
    def on_mouse_release(x, y, buttons, modifiers): 
        game.scene.on_mouse_release(x, y, buttons, modifiers)
    
    # output all events
    #game.win.push_handlers(pyglet.window.event.WindowEventLogger())
    
    # Start the game loop. 
    game.event_loop()
