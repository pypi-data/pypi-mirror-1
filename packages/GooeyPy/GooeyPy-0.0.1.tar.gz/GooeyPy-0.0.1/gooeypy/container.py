import pygame
import util
from const import *
import widget
import slider

from cellulose import *


class Container(widget.Widget):
    """
    Container([scrollable]) -> Container widget
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    A base container widget for containing other widgets. (gosh that's
    descriptive!) scrollable is for wether or not the container is, well,
    scrollable (actually, this feature doesn't work yet)!
    """

    scrollable = util.ReplaceableCellDescriptor()
    offset_x   = util.ReplaceableCellDescriptor()
    offset_y   = util.ReplaceableCellDescriptor()

    def __init__(self, scrollable=False, **params):
        widget.Widget.__init__(self, **params)
        self.widgets = CellList()
        self.scrollable = scrollable
        self.offset_x = 0
        self.offset_y = 0

        #self.vslider = slider.VSlider(length=1, step=False,
                #active=self.scrollable)
        #self.vslider.x = self.width - self.vslider.width
        #self.vslider.container = self
        #self.vslider.parent = self

    def draw_widget(self):
        for w in self.widgets:
            w.dirty = True

    def draw(self):
        widget.Widget.draw(self)
        for w in self.widgets:
            if w.active:
                w.draw()
        #if self.scrollable:
            #self.vslider.draw()

    def exit(self):
        self.hovering = False
        for w in self.widgets:
            w.exit()

    def event(self,e):
        for w in self.widgets:
            if w.active:
                w._event(e)

    def add(self, widgets):
        """
        Container.add(widgets) -> None
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
        Add widgets to Container.

        Arguments
        ---------
        widgets
            can ether be a single widget or a list of widgets.
        """
        if type(widgets) != list:
            widgets = [widgets]

        for w in widgets:
            self.widgets.append(w)
            w.container = self
            w.parent = self

    def remove(self, widgets):
        """
        Container.remove(widgets) -> None
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
        Remove widgets from Container.

        Arguments
        ---------
        widgets
            can ether be a single widget or a list of widgets.

        """
        if type(widgets) != list:
            widgets = [widgets]
        for w in widgets:
            self.widgets.remove(w)

    def _next(self,orig=None):
        start = 0
        if orig and orig in self.widgets: start = self.widgets.index(orig)+1
        for w in self.widgets[start:]:
            if not w.disabled and w.focusable:
                if isinstance(w,Container):
                    if w._next():
                        return True
                else:
                    self.focus(w)
                    return True
        return False

    def next(self,w=None):
        if self._next(w): return True
        if self.container: return self.container.next(self)