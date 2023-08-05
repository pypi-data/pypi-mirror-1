import pygame
from pygame.locals import *
import util
from const import *
import widget

from cellulose import *
from cellulose.restrictions import StringRestriction


class Label(widget.Widget):
    """
    Label(value) -> Label widget
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    Basic widget for simply displaying some text. Not really much to
    it, you can pass it a value which it will display.
    """
    value = util.ReplaceableCellDescriptor(restriction=StringRestriction())

    def __init__(self, value, **params):
        widget.Widget.__init__(self, **params)

        self.value = value

    @ComputedCellDescriptor
    def font(self):
        """
        Label.font -> pygame.Font
        ^^^^^^^^^^^^^^^^^^^^^^^^^
        The font that this label is using.
        """
        f = util.app.get_font(self.style_option["font-family"], self.style_option["font-size"])
        if self.style_option["font-weight"] == "bold":
            f.set_bold(True)
        return f

    @ComputedCellDescriptor
    def width(self):
        w = self.font.size(self.value)[0]+self.style_option["padding-left"]+\
                self.style_option["padding-right"]
        return widget.Widget.width.function(self, w)

    @ComputedCellDescriptor
    def height(self):
        h = self.font.size(self.value)[1]+self.style_option["padding-top"]+\
                self.style_option["padding-bottom"]
        return widget.Widget.height.function(self, h)

    @ComputedCellDescriptor
    def font_x(self):
        x,_ = self.pos
        return x + self.style_option["padding-left"]
    @ComputedCellDescriptor
    def font_y(self):
        _,y = self.pos
        return y + self.style_option["padding-top"]

    @ComputedCellDescriptor
    def clip_rect(self):
        return pygame.Rect(0,0,
                self.width-(self.style_option["padding-left"]+\
                self.style_option["padding-right"]),
                self.height-(self.style_option["padding-top"]+\
                self.style_option["padding-bottom"]))


    def draw_widget(self):
        # We do this incase we are trying to blit the text into a space smaller
        # than it can fit into.

        util.blit(self.font.render(self.value, 1, self.style_option["color"]),
                (self.font_x,self.font_y), clip_rect=self.clip_rect)