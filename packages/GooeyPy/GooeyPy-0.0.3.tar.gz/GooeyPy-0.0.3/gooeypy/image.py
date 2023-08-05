import pygame
from pygame.locals import *
import util
from const import *
import widget

from cellulose import *


class Image(widget.Widget):
    """
    Image(value) -> Image widget
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    Basic widget for simply displaying an image. value should be a pygame
    surface.
    """
    value = util.ReplaceableCellDescriptor()

    def __init__(self, value, **params):
        widget.Widget.__init__(self, **params)
        self.value = value

    def draw_widget(self):
        util.blit(self.value, self.pos, clip_rect=self.value.get_rect())


    def height(self):
        h = self.value.get_height() + self.style_option["padding-bottom"]+\
                self.style_option["padding-top"]
        return widget.Widget.height.function(self, h)
    height = ComputedCellDescriptor(height)

    def width(self):
        w = self.value.get_width() + self.style_option["padding-right"]+\
                self.style_option["padding-left"]
        return widget.Widget.width.function(self, w)
    width = ComputedCellDescriptor(width)