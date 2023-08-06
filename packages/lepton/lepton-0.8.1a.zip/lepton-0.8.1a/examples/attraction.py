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
""" Attraction.

    Demos the attract controller. Electrons orbit protons.

    Note: electrons do not really orbit protons via an inverse square
    force law. If they did they would radiate energy and eventually
    collide with the nucleus. 

"""

__version__ = '$Id: attraction.py 104 2008-11-08 06:49:41Z andrew.charles $'

from pyglet import image
from pyglet.gl import *

from lepton import Particle, ParticleGroup, default_system
from lepton.renderer import PointRenderer
from lepton.emitter import StaticEmitter, PerParticleEmitter
from lepton.controller import Movement, Bounce, Attractor, Lifetime,Fader, ColorBlender
from lepton.domain import AABox, Sphere
from random import uniform, gauss

if __name__ == '__main__':
    win = pyglet.window.Window(resizable=True, visible=False)
    win.clear()

    def resize(widthWindow, heightWindow):
        """Initial settings for the OpenGL state machine, clear color, window size, etc"""
        glEnable(GL_BLEND)
        glEnable(GL_POINT_SMOOTH)
        glShadeModel(GL_SMOOTH)# Enables Smooth Shading
        glBlendFunc(GL_SRC_ALPHA,GL_ONE)#Type Of Blending To Perform
        glHint(GL_POINT_SMOOTH_HINT,GL_NICEST);#Really Nice Point Smoothing
        glDisable(GL_DEPTH_TEST)
    
    electron_count = 12 
    electron_size = 15
    proton_size =25 
    n_protons = 2

    # Random colour trails
    lifetime = 5 

    # Screen domain is a box the size of the screen
    screen_domain = AABox((electron_size/2.0, electron_size/2.0, 0), 
    (win.width-electron_size/2.0,win.height-electron_size/2.0,0))

    # The central attractor

    # Attractor
    protons=[]
    spheres=[]
    for i in range(n_protons): 
        sphere = Sphere((((i+1)/3.)*win.width,((i+1)/3.)*win.height,0.0),proton_size)
        proton = Attractor(sphere, g=5000.0,mass=3.0)
        proton.color = (0.1,0.7,0.1)
        protons.append(proton)
        spheres.append(sphere)

    
    default_system.add_global_controller(
        Movement(max_velocity=200), 
        Bounce(screen_domain,bounce=0.5,friction=0.1),
        # Bounce on collision with attractors
        # Negative tangential friction to 'spin' collisions off.
        Bounce(spheres[0],bounce=0.5,friction=-0.2),
        Bounce(spheres[1],bounce=0.5,friction=-0.2),
        *protons
    )

    group = ParticleGroup(renderer=PointRenderer(point_size=electron_size))
       
    # Trails for electrons 
    electron_emitter = StaticEmitter(
        position=screen_domain,
        rate=1,
        deviation=Particle(velocity=(20,20,0), color=(0.0,0.0,0.0,0)),
        color=[(0.5,0.5,0.9,1)],
    )
    electron_emitter.emit(electron_count, group)
    group.update(0)

    trail_emitter = PerParticleEmitter(group,rate=uniform(5,20),
            template=Particle(
                color=(uniform(0,1), uniform(0,1), uniform(0,1), 1),
                size=(0.2,0.2,0)),
                deviation=Particle(
                velocity=(1,1,1),
                size=(2.5,2.5,0),
                age=lifetime * 0.75))

    trails = ParticleGroup(
            controllers=[
                Lifetime(lifetime * 1.5),
                Movement(damping=0.83),
                Fader(fade_out_start=0, fade_out_end=gauss(lifetime, lifetime*0.3)),
                trail_emitter],
             renderer=PointRenderer(point_size=2)
             )

    def emit(dt):
        electron_emitter.emit(electron_count, group)
            
    win.resize = resize
    win.set_visible(True)
    win.resize(win.width, win.height)
    pyglet.clock.schedule_interval(default_system.update, (1.0/30.0))

    def draw_protons():
        glPointSize(protons[0].domain.radius)
        glBegin(GL_POINTS)
        for proton in protons:
            cx, cy, cz = proton.domain.center
            glColor3f(*proton.color)
            glVertex3f(cx, cy, cz)
        glEnd()

    @win.event
    def on_draw():
        global i
        win.clear()
        glLoadIdentity()
        k = uniform(0,0.1)
        draw_protons()
        default_system.draw()

    pyglet.app.run()

