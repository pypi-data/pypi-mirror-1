#!/usr/bin/env python
# -*- coding: utf-8 -*-
# encoding: utf-8

"""A fungus blob swarm.

Ideas: 
- Use a lightweight sprite instead of the normal core sprite to avoid unecessary overhead. 

"""

#### Imports ####

from fungus_core import Sprite
from fungus_scene import BaseScene

from os.path import join, dirname

from random import random, choice, randint

# Reduce CPU usage: sleep
from time import sleep

#### Constants ####

NUMBER_OF_BLOBS = 100

SEARCH_DISTANCE = 20
MAX_SEARCH_DISTANCE = 2**32 # 32 bit integer - avoids massive slowdowns
MAX_FLIGHT_STEP = 2.0
STEPS_TO_FLEE = 20
#: Do we want to never choose the last partner as next partner? 
NEVER_SELECT_LAST_AS_NEXT = False
# The distribution of sexes among the blobs. 
SEX_DISTRIBUTION = ["male", "male", "female", "female", None]
#SEX_DISTRIBUTION = ["male", None]
#SEX_DISTRIBUTION = ["male", "female"]
#SEX_DISTRIBUTION = ["male", "female", None, None, None]
#SEX_DISTRIBUTION = ["male", "male", "male", "male", "male", "female", None]
#: Strengths of random movement
RANDOM_MOVEMENT = 0.5
#: Strength of individual bias in random movement. 
BIASED_RANDOM_MOVEMENT = 4.0
#: Inverse speed towards the partner. This should be at most 20 / RANDOM_MOVEMENT
# (less if they have a strong bias), else the blobs get in danger of never touching. 
SPEED_TOWARDS_PARTNER_INVERSE = 10
#: Where Blobs start. "random", "sex seperated", None (None is the default position for Sprites)
STARTING_POSITIONS = "random"
#: Which sex is compatible with which
COMPATIBLE_SEXES = {
    None: ["male", "female", None],
    "male": ["female", None],
    "female": ["male", None]
}

UNBONDED = {}
for sex in SEX_DISTRIBUTION: 
    if not sex in UNBONDED: 
	UNBONDED[sex] = []

#### An example scene ####

### Things needed for the scene

IMAGE_BASE_PATH = join(dirname(__file__), "graphics")

class Blob(Sprite): 
	"""One of the moving blobs.
	
	Ideas: 
		- sex = None => hostile; no sexual interest
		- sex = undecided => what None currently does
		"""
	#: Blobs without partner
	_unbonded = UNBONDED
	def __init__(self, sex=None, *args, **kwds): 
		if sex is None: 
			super(Blob, self).__init__(image_path=join(IMAGE_BASE_PATH, "blobn.png"), *args, **kwds)
		elif sex=="female":
			super(Blob, self).__init__(image_path=join(IMAGE_BASE_PATH, "blobf.png"), *args, **kwds)
		else: # male
 			super(Blob, self).__init__(image_path=join(IMAGE_BASE_PATH, "blob.png"), *args, **kwds)
		#: The one to move towards
		self.partner = None
		#: The last partner
		self.last_partner = None
		#: Sexual orientation: Either male, female or undecided (None). 
		self.sex = sex
		
		self.steps_to_flee = 0
		
		# Controlling parameters
		self.max_flight_step = MAX_FLIGHT_STEP
		self.search_distance = SEARCH_DISTANCE #: x**2 + y**2
		#: Safe distance: If a partner comes close than this, we run away. 
		# 2 * radius**2, since we have to take the radius of the partner into account, too. 
		self.safe_distance = (self.width**2 + self.height**2) / 2.0
		#: Biase of random movement into x direction
		self.x_bias = (random() - 0.5) * BIASED_RANDOM_MOVEMENT
		#: Biase of random movement into y direction
		self.y_bias = (random() - 0.5) * BIASED_RANDOM_MOVEMENT
		
		self.compatible_sexes = COMPATIBLE_SEXES[self.sex]
		
		
		#: Continuous movement
		self.dx = 0
		self.dy = 0
		
		# Put outself in the Blobs and the unbonded class list
		self._unbonded[self.sex].append(self)
		
	def distance_to(self, other): 
		"""Squared distance to the partner. Calculated from the centers."""
		x = (other.x + 0.5*other.width) - (self.x + 0.5*self.width)
		y = (other.y + 0.5*other.height) - (self.y + 0.5*self.height)
		return x**2 + y**2
	
	def is_valid_partner_for(self, other): 
		"""Check, if we are a valid partner for the other blob.
		
		We don't check the sex, since the blob only looks among blobs with fitting sex."""
		# don't bond with yourself
		if other is self: 
		    return False
		# Never choose the last partner as next partner. 
		if NEVER_SELECT_LAST_AS_NEXT and self.last_partner is other: 
			return False
		# Valid partners have to be in the search distance
		if self.distance_to(other) > self.search_distance: 
			return False
		return True
	
	def flee(self): 
		"""Jump one random step away."""
		# First set the direction
		self.dx += (2*random() - 1.0) * self.max_flight_step
		self.dy += (2*random() - 1.0) * self.max_flight_step
		# Then do the movement, multiplied with the number of steps we still have to run
		# (this gives continuous and slowing movement)
		self.x += self.dx
		self.y += self.dy
		# And reduce the steps to flee
		self.steps_to_flee -= 1
		
		if not self.steps_to_flee: 
		    # Stop the continuous movement if we reached the end of our flight.
		    self.dx = self.dy = 0
		    # Also add ourselves to the unbonded list. 
		    self._unbonded[self.sex].append(self)
		
	def update(self): 
		self.move_random()
		if self.steps_to_flee: 
			self.flee()
		elif self.partner is None: 
			self.search_partner()
		else: 
			self.move_towards_partner()
			self.is_partner_too_close()
	
	def move_random(self): 
		"""Random movement."""
		if BIASED_RANDOM_MOVEMENT: 
		    self.x += (2*random() - 1.0 + self.x_bias) * RANDOM_MOVEMENT
		    self.y += (2*random() - 1.0 + self.y_bias) * RANDOM_MOVEMENT
		else: 
		    self.x += (2*random() - 1.0) * RANDOM_MOVEMENT
		    self.y += (2*random() - 1.0) * RANDOM_MOVEMENT
	
	def search_partner(self): 
		"""Check if there's a compatible partner in range."""
		for sex in self.compatible_sexes: 
			for other in self._unbonded[sex]: 
				if self.is_valid_partner_for(other): 
					# bond
					self.partner = other
					other.partner = self
					self._unbonded[self.sex].remove(self)
					self._unbonded[other.sex].remove(other)
					# reduce search distance of both
					self.search_distance = SEARCH_DISTANCE
					other.search_distance = SEARCH_DISTANCE
					return
		
		# If we don't find a partner, increase the search distance, 
		# but make sure it doesn't grow without bounds. 
		# grow it if it's smaller than the MAX_SEARCH_DISTANCE
		if self.search_distance < MAX_SEARCH_DISTANCE:
		    self.search_distance *= self.search_distance
		# and shrink it down if that made it larger. 
		elif self.search_distance > MAX_SEARCH_DISTANCE: 
		    self.search_distance = MAX_SEARCH_DISTANCE
		    # Now it won't be increased, since it is exactly the MAX_SEARCH_DISTANCE
		    # and none of the two if clauses will catch
		
		
		
	def move_towards_partner(self): 
		"""Walk 10% of the way towards your partner."""
		self.x += (self.partner.x - self.x ) / SPEED_TOWARDS_PARTNER_INVERSE
		self.y += (self.partner.y - self.y ) / SPEED_TOWARDS_PARTNER_INVERSE
		
	
	def break_bond(self): 
		"""Break the partnership."""
		# Run away
		self.steps_to_flee = STEPS_TO_FLEE
		# Tell the partner to run away
		self.partner.steps_to_flee = STEPS_TO_FLEE
		# Mark the partner as last partner
		self.partner.last_partner = self
		self.last_partner = self.partner
		# And break the bond, but not yet add to unbonded
		self.partner.partner = None
		self.partner = None
		
	def is_partner_too_close(self): 
		"""If the partner did come too close."""
		if self.distance_to(self.partner) < self.safe_distance: 
			self.break_bond()
		
		
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
        
        ## Tests - not necessary for every scene. 
        # Add a tank to the visible items. 	
        self.blobs = []
        for i in range(NUMBER_OF_BLOBS):
		sex=choice(SEX_DISTRIBUTION)
		x, y = self.get_starting_position(sex)
        	blob = Blob(x=x, y=y, sex=sex)
        	self.blobs.append(blob)
        	self.visible.append(blob)
        	
    
     
    def keep_on_screen(self, blob): 
		if blob.x < 0: 
			blob.x = 0
			 
		if blob.y < 0: 
			blob.y = 0
			 
		if blob.x + blob.width > self.core.win.width: 
			blob.x = self.core.win.width - blob.width
			 
		if blob.y + blob.height > self.core.win.height: 
			blob.y = self.core.win.height - blob.height


		
    def get_starting_position(self, sex): 
		"""Select a starting position based on the config parameters."""
		# Start at a fixed position
		if STARTING_POSITIONS is None: 
			x = 0.5 * self.core.win.width
			y = 0.5 * self.core.win.height
		# Start at random positions
		elif STARTING_POSITIONS == "random": 
			x = random() * self.core.win.width
			y = random() * self.core.win.height
		# Or sex seperated
		elif STARTING_POSITIONS == "sex seperated": 
			if sex is None: 
				pos_x = 0.0
				pos_y = 1.0
			elif sex == "male": 
				pos_x = pos_y = 1.0
			else: 
				pos_x = pos_y = 0.0
			x = pos_x * self.core.win.width
			y = pos_y * self.core.win.height
		return x, y
		

    def update(self): 
        """Update the stats of all scene objects. 

Don't blit them, though. That's done by the Game itself.

To show something, add it to the self.visible list. 
To add a collider, add it to the self.colliding list. 
To add an overlay sprite, add it to the self.overlay list. 
"""
        for blob in self.blobs: 
        	blob.update()
		self.keep_on_screen(blob)
	# sleep for a blink, so we don't always max out the CPU
	sleep(0.01)
