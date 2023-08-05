""" <title>Styling options</title> """
import util
import pygame

from cellulose import *

class StyleSet(object):
    """
    StyleSet(widget, [parent]) -> StyleSet object
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    A styleset is a collection of style options grouped together for a
    specific event for a widget. Each widget has an dictionary named
    "stylesets" which contains several stylesets. For example::

        {"disabled":styleset, "hover":styleset, "default":styleset,
                "focused":styleset, "down":styleset}

    When the widget is hovered for example it will use stylesets["hover"]
    At any time you can change a styling option for a widget by doing
    something like this::

        mywidget.stylesets["hover"]["color"] = (255,10,10)

    **WARNING:** Do not use the color (0,0,0)! It is used as the surface color
    key. That means that if you use it it won't show up! If you want to use the
    color black, use (5,5,5) or something (which is indistinguishable from pure
    black). This applies to font colors sometimes. :P

    Style options
    -------------

    ===============  =======================================================
    option           value
    ===============  =======================================================
    padding          8 4 4 5 | 4 5 | 10
    padding-top      3
    padding-right    3
    padding-bottom   3
    padding-left     3
    color            (255,255,255)
    font-weight      normal | bold
    font-family      Verra.ttf
    font-size        12
    effect           pulsate 5
    width            300
    height           200
    x                57
    y                102
    position         relative | absolute
    bgcolor          (200,0,0)
    bgimage          image.png repeat|repeat-x|repeat-y|no-repeat|slice
    border           (0,250,20) 3
    spacing          12 # For certain container widgets.
    opacity          25 # Alpha value. Valid otpions between 0 and 255.
    antialias        1 | 0
    align            left | right | center
    valign           top | bottom | center
    ===============  =======================================================

    Something to note about align and valign. When they are changed from their
    default values (top and left), the x and y values act as an offset. So if
    you are aligning a widget center and have an x value of 100, the widget will
    display 100 pixels to the right of the center of it's parent (or container)
    widget.

    Also, aligning only takes effect when positioning is relative (which is
    default).


    Arguments
    ---------
    widget
        The widget this styleset is for.

    parent
        Another styleset that this styleset should inherit from.
    """

    parent = util.ReplaceableCellDescriptor()
    widget = util.ReplaceableCellDescriptor()

    # Setting a default style option here will make it use it at all times
    # unless explicitly set. In other words, inheriting doesn't work for these
    # options.
    default_styles = {
        "padding-top":0,
        "padding-right":0,
        "padding-bottom":0,
        "padding-left":0,
        "spacing":0,
        #"color":(10,10,10),
        "font-weight":"normal",
        #"font-size":12,
        "effect":"none",
        "width":util.screen_width,
        "height":util.screen_height,
        "x":0,
        "y":0,
        "position":"relative",
        #"align":"left",
        #"valign":"top",
        }

    def __init__(self, widget, parent=None):
        self.widget = widget
        self.parent = parent
        self._applied_styles = CellDict(self.default_styles)

        def __getitem__(v):
            return self.__getitem__(v)
        self._applied_styles.__getitem__ = __getitem__

    # We make this read only so people can only modify the applied_styles and
    # not reassign it.
    applied_styles = property(lambda self: self._applied_styles)


    def surf(self):
        """
        StyleSet.surf -> pygame.Surface
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
        The surface generated from the styling.
        """
        #print self
        if self.parent:
            s = self.parent.surf.copy()
        else:
            size = (int(self.widget.width), int(self.widget.height))
            s = pygame.Surface(size)
            s.set_colorkey((0,0,0,0))


        for (option, values) in self.applied_styles.items():
            s = self.apply(s, option, values)
        return s
    surf = ComputedCellDescriptor(surf)


    def __getitem__(self, v):
        r = None
        if self.applied_styles.has_key(v):
            r = self.applied_styles[v]
        if not r and self.parent:
            r = self.parent[v]
        if hasattr(r, "value"): r = r.value
        return r

    def __setitem__(self, k, v):
        #self.applied_styles[k] = v
        self.apply(None, k, v)

    def __cmp__(self, other):
        if isinstance(other, self.__class__):
            if other.applied_styles == self.default_styles or\
                    self.applied_styles == self.default_styles:
                return 0
            if self.applied_styles == other.applied_styles:
                return 0
        return -1


    def apply(self, surf, option, values):
        """
        StyleSet.apply(surf, option, values) -> pygame.Surface
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
        Applies styling to surf. If you are just wanting to change a style
        option, use::

            StyleSet["option"] = values

        This function is mainly for internal use.
        """
        option = option.replace("_", "-")
        o = option.replace("-", "_")
        if type(values) == str or type(values) == int:
            if type(values) == str:
                values = values.split(" ")
            else: values = [values]
        if hasattr(self, o):
            o = getattr(self, o)
            if callable(o):
                surf = o(surf, values)
        else:
            surf = self.generic(surf, option, values)
        return surf


    def generic(self, surf, n, v):
        if type(v) == list:
            if len(v) == 1:
                v = v[0]
                v = str(v)
                # For some reason isdigit returns False if v is something like
                # '-20'. FIX?
                if v.isdigit(): v = int(v)
        self.applied_styles[n] = v
        return surf

    def effect(self, surf, values):
        if len(values) == 1 and values[0] != "none":
            values.append("10")
        self.applied_styles["effect"] = values
        return surf

    def opacity(self, surf, values):
        if len(values) == 1:
            values = values[0]
        values = int(values)
        if surf:
            surf.set_alpha(values)
        self.applied_styles["opacity"] = values
        return surf


    def bgcolor(self, surf, values):
        #if self.applied_styles.has_key("bgcolor"):
            #return
        if surf and values[0] != "none":
            if type(values[0]) == str:
                color = values[0][1:-1].split(",")
                color = [int(c) for c in color]
            else:
                color = values[0]
            rect = surf.get_rect()

            # If there is a border, need to scale down so it doesn't
            # overlap it.
            if self.applied_styles.has_key("border"):
                w = int(self.applied_styles["border"][0])
                rect.x += w
                rect.y += w
                rect.width -= w*2
                rect.height -= w*2

            util.draw_rect(surf, color, rect)

        self.applied_styles["bgcolor"] = values
        return surf


    def border(self, surf, values):
        if surf:
            color = values[1][1:-1].split(",")
            color = [int(c) for c in color]
            width = int(values[0])

            util.draw_rect(surf, color, surf.get_rect(), width)

        self.applied_styles["border"] = values
        return surf

    def bgimage(self, surf, values):
        if values[0] == "none": return
        self.applied_styles["bgimage"] = values
        if not surf: return
        im = util.app.get_image(values[0])
        style = None
        if len(values) > 1:
            style = values[1]
        if not style or style == "no-repeat":
            surf.blit(im, (0,0))

        if style == "repeat" or style == "repeat-x"\
        or style == "repeat-y":
            num_x = surf.get_width() / im.get_width() +\
                    im.get_width()
            num_y = surf.get_height() / im.get_height() +\
                    im.get_height()

            if style == "repeat-y":
                for n in xrange(num_y):
                    x = 0
                    y = n*im.get_height()
                    surf.blit(im, (x,y))
            elif style == "repeat-x":
                for n in xrange(num_x):
                    x = n*im.get_width()
                    y = 0
                    surf.blit(im, (x,y))
            elif style == "repeat":
                for x in xrange(num_x):
                    for y in xrange(num_y):
                        xx = x*im.get_width()
                        yy = y*im.get_height()
                        surf.blit(im, (xx,yy))

        elif style == "slice":
            w = im.get_width()/2 - 1
            h = im.get_height()/2 - 1
            tl = im.subsurface((0, 0, w, h))
            bl = im.subsurface((0, im.get_height()-h, w, h))
            tr = im.subsurface((im.get_width()-w, 0, w, h))
            br = im.subsurface((im.get_width()-w, im.get_height()-h, w, h))
            l = im.subsurface((0, h, w, 2))
            r = im.subsurface((im.get_width()-w, h, w, 2))
            t = im.subsurface((w, 0, 2, h))
            b = im.subsurface((w, im.get_height()-h, 2, h))
            c = im.get_at((w+1, h+1))

            num_x = surf.get_width()  / t.get_width() + 1
            num_y = surf.get_height() / l.get_height() + 1

            pygame.draw.rect(surf, c, surf.get_rect())
            for x in xrange(num_x):
                surf.blit(t, (x*t.get_width(), 0))
                surf.blit(b, (x*t.get_width(), surf.get_height()-t.get_height()))
            for y in xrange(num_y):
                surf.blit(l, (0, y*l.get_height()))
                surf.blit(r, (surf.get_width()-r.get_width(), y*r.get_height()))
            surf.blit(tl, (0,0))
            surf.blit(bl, (0,surf.get_height()-h))
            surf.blit(tr, (surf.get_width()-w,0))
            surf.blit(br, (surf.get_width()-w,surf.get_height()-h))

        self.applied_styles["bgimage"] = values
        return surf

    def color(self, surf, values):
        if len(values) != 3:
            color = values[0][1:-1].split(",")
            color = [int(c) for c in color]
        else: color = values

        self.applied_styles["color"] = color
        return surf


    def padding(self, surf, values):
        padding = {}
        if len(values) == 1:
            top = right = bottom = left = values[0]
        elif len(values) == 2:
            top = bottom = values[0]
            left = right = values[1]
        elif len(values) == 4:
            top, right, bottom, left = values

        padding["top"] = int(top)
        padding["right"] = int(right)
        padding["bottom"] = int(bottom)
        padding["left"] = int(left)

        for k in ("top", "left", "right", "bottom"):
            key = "padding-"+k
            if not self.applied_styles[key]:
                self.applied_styles[key] = padding[k]
        return surf