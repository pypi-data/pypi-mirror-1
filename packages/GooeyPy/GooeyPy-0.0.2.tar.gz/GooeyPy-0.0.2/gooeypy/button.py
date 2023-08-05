import pygame
import util
from const import *
from pygame.locals import *
import widget, label

from cellulose.restrictions import StringRestriction
from cellulose import *


class _button(widget.Widget):

    _label = util.ReplaceableCellDescriptor()

    def __init__(self, **params):
        self._label = None
        widget.Widget.__init__(self, **params)


    def set_label(self, v):
        if hasattr(v, "value"):
            l = label.Label(v.value, parent=self)
            l._cells["value"] = ComputedCell(lambda:str(v.value))
        if type(v) == int:
            v = str(v)
        if type(v) == str:
            l = label.Label(v, parent=self)
        self.send(CHANGE)
        self._label = l
        self._label._cells["hovering"] = self._cells["hovering"]
        self._label._cells["focused"] = self._cells["focused"]
        self._label._cells["pressing"] = self._cells["pressing"]
    label = property(lambda self: self._label, set_label)

    @ComputedCellDescriptor
    def width(self):
        w = self.label.width + self.style_option["padding-left"]+self.style_option["padding-right"]
        return widget.Widget.width.function(self, w)

    @ComputedCellDescriptor
    def height(self):
        h = self.label.height + self.style_option["padding-top"]+self.style_option["padding-bottom"]
        return widget.Widget.height.function(self, h)


    def draw_widget(self):
        self.label.dirty = True
        self.label.draw()



class Button(_button):
    """
    Button([value]) -> Button widget
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    A widget resembling a button.

    Arguments
    ---------
    value
        The text or widget to be displayed on the button.
    """

    _value = util.ReplaceableCellDescriptor()

    def __init__(self, value=" ", **params):
        _button.__init__(self, **params)
        self._value = None
        self.set_value(value)

    def set_value(self, v):
        self._value = v
        self.label = v

    value = property(lambda self: self._value, set_value)



class Switch(_button):
    """
    Switch([value, [on_label, [off_label]]]) -> Switch widget
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    This is very similar to a button except the value will always be ether
    True or False

    Arguments
    ---------
    value
        You can set it to True or False (default).

    on_label
        The text displayed when the switch is on.

    off_label
        The text displayed when the switch is off.
    """

    _value = util.ReplaceableCellDescriptor()
    on_label = util.ReplaceableCellDescriptor()
    off_label = util.ReplaceableCellDescriptor()

    def __init__(self, value=False, on_label="on", off_label="off", **params):
        _button.__init__(self, **params)
        self._value = value
        self.on_label = on_label
        self.off_label = off_label
        self.set_value(value)


    def set_value(self, v):
        self._value = v
        if v == True:
            self.label = self.on_label
        else:
            self.label = self.off_label
    value = property(lambda self: self._value, set_value)

    def click(self):
        self.value = not self.value
        self.send(CHANGE)