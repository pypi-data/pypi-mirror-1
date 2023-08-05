from __future__ import division

import rabbyt
from rabbyt.vertexarrays import VertexArray
from rabbyt.sprites import BaseSprite

import pygame

default_alphabet = ("0123456789"
                    "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
                    "abcdefghijklmnopqrstuvwxyz"
                    "{}()[]<>!?.,:;'\"*&%$@#\/|+=-_~`")

class Font(object):
    def __init__(self, pygame_font, alphabet=default_alphabet):
        self.pygame_font = pygame_font
        self.alphabet = default_alphabet
        width = sum([self.pygame_font.size(char)[0]+1 for char in alphabet])
        height = self.pygame_font.size(" ")[1]

        surface = pygame.Surface((width, height), pygame.SRCALPHA)

        self.coords = {}
        x=0
        for char in alphabet:
            w = self.pygame_font.size(char)[0]
            self.coords[char] = (x/width, (x+w)/width)
            surface.blit(self.pygame_font.render(char, True, (255,255,255)), (x,0))
            x += w+1

        data = pygame.image.tostring(surface, "RGBA", True)
        self.texture_id = rabbyt.load_texture(data, (width, height))
        self.height = height
        self.space_width = pygame_font.size(" ")[0]

    def get_char_tex_shape(self, char):
        l, r = self.coords[char]
        return l, 1, r, 0

    def get_char_width(self, char):
        return self.pygame_font.size(char)[0]

class FontSprite(BaseSprite):
    def __init__(self, font, text, **kwargs):
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
    text = property(_get_text, _set_text)

    def render_after_transform(self):
        rabbyt.set_gl_color(self.rgba)
        self.va.render()

