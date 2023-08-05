"""
Rabbyt is a fast 2d sprite library for Python.
"""


__credits__ = (
"""
Copyright (C) 2007  Matthew Marshall

This library is free software; you can redistribute it and/or
modify it under the terms of the GNU Library General Public
License as published by the Free Software Foundation; either
version 2 of the License, or (at your option) any later version.

This library is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
Library General Public License for more details.

You should have received a copy of the GNU Library General Public
License along with this library; if not, write to the Free
Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
""")

__author__ = "Matthew Marshall <matthew@matthewmarshall.org>"
__version__ = "0.0.1"

import heapq

from _rabbyt import *

extend_types = dict(constant=1, extrapolate=2, repeat=3, reverse=4)

def _handle_time_args(startt, endt, dt):
    if startt is None:
        startt = get_time()
    if endt is None:
        if dt is None:
            raise ValueError("Either dt or endt must be given.")
        endt = startt + dt

    assert startt < endt

    return int(startt), int(endt)


def lerp(start, end, startt=None, endt=None, dt=None, extend="constant"):
    extend = extend_types[extend]

    startt, endt = _handle_time_args(startt, endt, dt)

    try:
        iter(start), iter(end)
    except TypeError:
        return AnimLerp(start, end, startt, endt, extend)
    else:
        return [AnimLerp(s, e, startt, endt, extend)
                for s,e in zip(start, end)]

def wrap(bounds, parent, static=True):
    try:
        iter(parent)
    except TypeError:
        return AnimWrap(bounds, parent, static)
    else:
        return tuple([AnimWrap(bounds, p, static) for p in parent])

def bezier3(p0, p1, p2, p3, startt=None, endt=None, dt=None, extend="constant"):
    extend = extend_types[extend]
    startt, endt = _handle_time_args(startt, endt, dt)

    try:
        [iter(p) for p in [p0,p1,p2,p3]]
    except TypeError:
        return AnimStaticCubicBezier(p0, p1, p2, p3, startt, endt, extend)
    else:
        return [AnimStaticCubicBezier(p0, p1, p2, p3, startt, endt, extend)
                for p0, p1, p2, p3 in zip(p0, p1, p2, p3)]


class Scheduler(object):
    """
    Scheduler provides... (wait for it...)  scheduling!

    You may create your own scheduler instances, or use the default
    ``rabbyt.scheduler``
    """
    def __init__(self):
        self.heap = []

    def add(self, time, callback):
        """
        add(time, callback)

        Schedules a callback to be called at a given time.
        """
        heapq.heappush(self.heap, (time, callback))

    def pump(self, time=None):
        """
        pump([time])

        Calls all callbacks that have been scheduled for before 'time'

        If 'time' is not given, the value returned by rabbyt.get_time() will be
        used.
        """
        if time is None:
            time = get_time()
        try:
            while self.heap[0][0] <= time:
                heapq.heappop(self.heap)[1]()
        except IndexError, e:
            # If the IndexError was raised due to something other than an
            # empty heap we don't want to silence it.
            if len(self.heap) != 0:
                raise e

scheduler = Scheduler()


def init_display(size=(640, 480)):
    """
    init_display(size=(640, 480))

    This is a small shortcut to create a pygame window, set the viewport, and
    set the opengl attributes need for rabbyt.

    This function depends on pygame.
    """
    import pygame
    pygame.display.set_mode(size, pygame.OPENGL | pygame.DOUBLEBUF)
    set_viewport(size)
    set_default_attribs()

_texture_cache = {}

def pygame_load_texture(filename):
    if filename not in _texture_cache:
        import pygame
        img = pygame.image.load(filename)
        data, size = pygame.image.tostring(img, 'RGBA', True), img.get_size()
        _texture_cache[filename] = load_texture(data, size), size
    return _texture_cache[filename]
set_load_texture_file_hook(pygame_load_texture)
