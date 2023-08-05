from __future__ import division

"""
rabbyt.fonts
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


import rabbyt
from rabbyt.vertexarrays import VertexArray
from rabbyt.sprites import BaseSprite

import pygame

default_alphabet = ("0123456789"
                    "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
                    "abcdefghijklmnopqrstuvwxyz"
                    "{}()[]<>!?.,:;'\"*&%$@#\/|+=-_~`")

def next_power_of_2(v):
    v = int(v)- 1
    v |= v >> 1
    v |= v >> 2
    v |= v >> 4
    v |= v >> 8
    v |= v >> 16
    return v + 1

class Font(object):
    """
    Font

    Holds the information for drawing a font.

    To actually draw a font you need to use a FontSprite.

    The characters will be rendered onto an OpenGL texture.
    """
    def __init__(self, pygame_font, alphabet=default_alphabet):
        """
        Font(pygame_font, [alphabet])

        pygame_font should be a pygame.font.Font instace.

        alphabet is a string containing all of the characters that should be
        loaded into video memory.  It defaults to rabbyt.fonts.default_alphabet
        which includes numbers, symbols, and letters used in the English
        language.
        """
        self.pygame_font = pygame_font
        self.alphabet = alphabet
        widest = max(self.pygame_font.size(char)[0]+1 for char in alphabet)
        height = self.pygame_font.size(" ")[1]

        total_area = widest*height*len(self.alphabet)
        sw = sh = total_area**.5
        sw += widest
        sh += height
        sw = next_power_of_2(sw)
        sh = next_power_of_2(sh)

        surface = pygame.Surface((sw, sh), pygame.SRCALPHA, 32)

        self.coords = {}
        x=0
        y=0
        for char in alphabet:
            w = self.pygame_font.size(char)[0]
            self.coords[char] = (x/sw, 1-y/sh, (x+w)/sw, 1-(y+height)/sh)
            surface.blit(
                    self.pygame_font.render(char, True, (255,255,255)), (x,y))
            x += widest
            if x + widest > sw:
                y += height
                x = 0

        data = pygame.image.tostring(surface, "RGBA", True)
        self._texture_id = rabbyt.load_texture(data, (sw, sh))
        self.height = height
        self.space_width = pygame_font.size(" ")[0]

    def _get_texture_id(self):
        return self._texture_id
    texture_id = property(_get_texture_id, doc=
        """
        This is the id of the OpenGL texture for this font.  The texture will
        be unloaded when the font is garbage collected.
        """)

    def get_char_tex_shape(self, char):
        """
        get_char_tex_shape(char)

        Returns the texture shape of the given character in the form of (left,
        top, right, bottom).

        KeyError is raised if char is not in the font's alphabet.
        """
        return self.coords[char]

    def get_char_width(self, char):
        """
        get_char_width(char)

        Returns the width in pixels of the given character.
        """
        return self.pygame_font.size(char)[0]

    def __del__(self):
        if rabbyt:
            rabbyt.unload_texture(self.texture_id)

class FontSprite(BaseSprite):
    """
    FontSprite

    A sprite that displays text from a Font.

    This inherits from BaseSprite, so you can use all of the transformation and
    color properties.
    """
    def __init__(self, font, text, **kwargs):
        """
        FontSprite(font, text, ...)

        font should be a rabbyt.fonts.Font instance to be used.

        text is the string to be displayed!  (It can be changed later with the
        text property.)
        """
        BaseSprite.__init__(self, **kwargs)
        self.font = font
        self.texture_id = font.texture_id
        self.text = text

    def _get_text(self):
        return self._text
    def _set_text(self, text):
        self._text = text
        va = VertexArray(use_colors=False)
        h = self.font.height
        x = 0
        for i, char in enumerate(text):
            if not char in self.font.alphabet:
                x += self.font.space_width
                continue
            w = self.font.get_char_width(char)
            l, t, r, b = self.font.get_char_tex_shape(char)
            va.append((x, 0, l, t))
            va.append((x+w, 0, r, t))
            va.append((x+w, -h, r, b))
            va.append((x, -h, l, b))
            x += w+1
        va.texture_id = self.texture_id
        self.va = va
    text = property(_get_text, _set_text, doc="the text to be displayed")

    def render_after_transform(self):
        rabbyt.set_gl_color(self.rgba)
        self.va.render()

