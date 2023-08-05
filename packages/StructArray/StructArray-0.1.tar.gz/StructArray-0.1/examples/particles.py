#!/usr/bin/env python

import random

from pyglet.window import *
from pyglet import clock
from pyglet import image
from pyglet.gl import *

from structarray import StructArray


class Particles(object):
    def __init__(self):
        # Unsigned bytes aren't implemented quite yet, so we'll use a single 4 byte
        # float for the color instead.  This works 'ok' with random colors.
        self.array = StructArray(['color', 'x', 'y', 'dx', 'dy'], size = 10000,
            defaults=(0,0,0,0,0))
        self.index = 0

    def render(self):
        glEnable(GL_BLEND)
        glBindTexture(GL_TEXTURE_2D, particle_image.texture.id)
        glPushClientAttrib(GL_CLIENT_VERTEX_ARRAY_BIT)
        glInterleavedArrays(GL_C4UB_V2F, self.array.get_data_stride(),
                self.array.get_data_addr())
        glDrawArrays(GL_POINTS, 0, len(self.array))
        glPopClientAttrib()

    def emit_particle(self):
        p = self.array[self.index]
        p.color = random.random()
        p.x, p.y = 512,200
        p.dx = random.random()*200 - 100
        p.dy = random.random()*190+10
        self.index += 1
        if self.index == len(self.array):
            self.index = 0

    def animate(self, dt):
        for i in range(5):
            self.emit_particle()
        self.array.x += self.array.dx*dt
        self.array.y += self.array.dy*dt
        self.array.dy -= 20*dt


window = Window(width=1024, height=768, vsync=False)
window.set_mouse_visible(False)

particle_image = image.load('particle.png')
glEnable(GL_TEXTURE_2D)

size = c_float()
glGetFloatv(GL_POINT_SIZE_MAX_ARB, byref(size))
glPointSize(min(16, size))

glTexEnvf(GL_POINT_SPRITE_ARB, GL_COORD_REPLACE_ARB, GL_TRUE)
glEnable(GL_POINT_SPRITE_ARB)

fps = clock.ClockDisplay(color=(1, .5, .5, 1))


particles = Particles()
clock.schedule(particles.animate)

glClearColor(0, 0, 0, 1)
while not window.has_exit:
    clock.tick()
    window.dispatch_events()

    glClear(GL_COLOR_BUFFER_BIT)

    particles.render()

    fps.draw()
    window.flip()

glDisable(GL_POINT_SPRITE_ARB)
