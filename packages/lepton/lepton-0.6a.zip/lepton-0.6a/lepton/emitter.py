#############################################################################
#
# Copyright (c) 2008 by Casey Duncan and contributors
# All Rights Reserved.
#
# This software is subject to the provisions of the MIT License
# A copy of the license should accompany this distribution.
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
#
#############################################################################
"""Particle Emitters

Particle emitters are a special type of particle controller
that adds particles to a group.
"""

__version__ = '$Id: emitter.py 132 2008-08-04 06:05:51Z casey.duncan $'

from particle_struct import Particle, Vec3, Color
from random import gauss, choice
from copy import copy

from _emitter import StaticEmitter

not_specified = object()

class PointEmitter(object):
	"""A simple particle emitter that emits particles based on a particle
	template, and randomized using a deviation template.

	Both the template and deviation particles may be mutated and/or replaced
	at runtime to move or otherwise change the emitter behavior dynamically.
	"""
	
	# Template particle used as basis for emitted particle attributes
	template = Particle()
	# Deviation particle used for randomizing the emitted particle attributes
	deviation = None
	# Discrete value dictionary used to specify multiple possible values
	# for particular particle attributes
	discrete = None
	expire_time = None

	def __init__(self, rate, template=not_specified, deviation=not_specified, 
		expire_time=None, **discrete):
		"""Initialize the emitter

		rate -- Emission rate in particles per unit time.
		
		template -- A Particle instance used as the basis (mathematical
		average) for the emitted particles' attributes.
		
		deviation -- A Particle instance used as the standard deviation for
		randomizing the particle attributes. If deviation is not specified
		then the emitted particles are exact clones of the template particle
		with no random deviation.

		expire_time -- If specified, the emitter will unbind itself from
		it's calling group after the specified time has accumulated. This
		allows you to schedule the emitter to stop participating in
		a group after a certain elapsed time.

		discrete -- Additional keyword arguments can be supplied to specify
		discrete values for particular particle attributes. These values
		override the cooresponding value in the template. The values may be
		supplied as a sequence of specific values, or as a domain instance (or
		any object with a generate method returning values).  This allows you
		to specify a discrete range of values that will be used uniformly for
		a particular attribute. Note the discrete values are still randomized
		by the deviation template the same way as the template values. 
		"""
		if template is not not_specified:
			self.template = template
		if deviation is not not_specified:
			self.deviation = deviation
		self.rate = float(rate)
		if discrete or self.discrete:
			if self.discrete:
				# meld in class-level discrete values
				discrete_copy = dict(self.discrete)
				discrete_copy.update(discrete)
				discrete = discrete_copy
			self.discrete = {}

			for name, values in discrete.items():
				if hasattr(values, 'generate'):
					# Values is a domain-like instance
					self.discrete[name] = values.generate
				else:
					if name in ('position', 'velocity', 'size', 'up', 'rotation'):
						values = [Vec3(*v) for v in values]
					elif name in ('mass', 'age'):
						values = [float(v) for v in values]
					elif name == 'color':
						values = [Color(*v) for v in values]
					else:
						raise ValueError('%s: Invalid discrete particle attribute %s'
							% (self.__class__.__name__, name))
					def generate(v=values):
						return choice(v)
					self.discrete[name] = generate
		self.partial = 0.0 # Partial particles emitted
		self.expire_time = expire_time
		self.elapsed_time = 0.0 # Total elapsed time of updates
	
	def make_particle(self, template, deviation=None):
		"""Return a particle based on the template particle randomized by 
		the deviation particle
		"""
		p = copy(template)
		if self.discrete:
			for name, generate in self.discrete.items():
				setattr(p, name, generate())
		if deviation is not None:
			p.position = Vec3(
				gauss(p.position.x, deviation.position.x),
				gauss(p.position.y, deviation.position.y),
				gauss(p.position.z, deviation.position.z))
			p.velocity = Vec3(
				gauss(p.velocity.x, deviation.velocity.x),
				gauss(p.velocity.y, deviation.velocity.y),
				gauss(p.velocity.z, deviation.velocity.z))
			p.size = Vec3(
				gauss(p.size.x, deviation.size.x),
				gauss(p.size.y, deviation.size.y),
				gauss(p.size.z, deviation.size.z))
			p.up = Vec3(
				gauss(p.up.x, deviation.up.x),
				gauss(p.up.y, deviation.up.y),
				gauss(p.up.z, deviation.up.z))
			p.rotation = Vec3(
				gauss(p.rotation.x, deviation.rotation.x),
				gauss(p.rotation.y, deviation.rotation.y),
				gauss(p.rotation.z, deviation.rotation.z))
			p.color = Color(
				gauss(p.color.r, deviation.color.r),
				gauss(p.color.g, deviation.color.g),
				gauss(p.color.b, deviation.color.b),
				gauss(p.color.a, deviation.color.a))
			p.mass = gauss(p.mass, deviation.mass)
			p.age = gauss(p.age, deviation.age)
			if p.age < 0:
				p.age = 0
		return p
	
	def emit(self, count, group):
		"""Emit the number of particles specified into the specified group"""
		for i in xrange(count):
			group.new(self.make_particle(self.template, self.deviation))
	
	def __call__(self, td, group):
		"""Emit the requisite particles into the supplied group, return the 
		number emitted. Note if the emission rate is low compared to the
		frequency of calls, this will often return 0
		"""
		# TODO Interpolate positions and possibly other attributes across calls
		if self.expire_time is not None:
			self.elapsed_time += td
			if self.elapsed_time >= self.expire_time:
				group.unbind_controller(self)
				# Adjust td to go just up to the expire time
				td -= self.elapsed_time - self.expire_time
		count = td * self.rate + self.partial
		emit_count = int(count)
		self.emit(int(count), group)
		self.partial = count - emit_count
		return emit_count
