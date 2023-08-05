import pygame
from pygame.locals import *
import util
from const import *
import widget

from cellulose import *
from cellulose.restrictions import StringRestriction


class TextBlock(widget.Widget):
    """
    TextBlock(value) -> TextBlock widget
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    Basic widget for wrapping and displaying some text. Currently doesn't
    support line breaks or anything, just text.
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
    def font_x(self):
        x,_ = self.pos
        return x + self.style_option["padding-left"]
    @ComputedCellDescriptor
    def font_y(self):
        _,y = self.pos
        return y + self.style_option["padding-top"]

    @ComputedCellDescriptor
    def font_value(self):
        # First we need to wrap the text (split it into lines).
        char_w,line_h = self.font.size("e")
        max_chars = self.style_option["width"]/char_w
        line_w,_ = self.font.size(max_chars*"e")
        words = self.value.split(" ")
        lines = []
        line_data = ""
        for word in words:
            if self.font.size(line_data +" "+ word)[0] < line_w:
                # We can fit this word onto this line.
                line_data = line_data+" "+word
            else:
                # Flush old line and start a new one.
                lines.append(line_data.strip())
                line_data = word
        lines.append(line_data.strip())

        surf = pygame.Surface((line_w, line_h*len(lines)))
        surf.set_colorkey((0,0,0,0))
        linenum = 0
        for line in lines:
            x = 0
            y = line_h*linenum
            surf.blit(self.font.render(line, self.style_option["antialias"],
                    self.style_option["color"]), (x,y))
            linenum += 1
        return surf

    @ComputedCellDescriptor
    def height(self):
        h = self.font_value.get_height() + self.style_option["padding-bottom"]+\
                self.style_option["padding-top"]
        return widget.Widget.height.function(self, h)

    def draw_widget(self):
        util.blit(self.font_value, (self.font_x,self.font_y))#,
                #clip_rect=self.clip_rect)