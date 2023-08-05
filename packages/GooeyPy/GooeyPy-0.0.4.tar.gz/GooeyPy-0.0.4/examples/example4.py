"""
Using GooeyPy with GL!
"""

import sys
sys.path.insert(0, "..")

import pygame
from gooeypy import gl as gui
from gooeypy.const import *

from OpenGL.GL import *

clock = pygame.time.Clock()

vw,vh = viewport = (640, 480)
pygame.display.set_mode(viewport, OPENGL | DOUBLEBUF)


# set up 2d mode
glMatrixMode(GL_PROJECTION)
glLoadIdentity()
glViewport(0, 0, vw, vh)
glOrtho(0, vw, 0, vh, -50, 50)
glMatrixMode(GL_MODELVIEW)
glLoadIdentity()
glDisable(GL_LIGHTING)
glDisable(GL_DEPTH_TEST)

glClearColor(0, 0, 0, 1)
glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE)
glEnable(GL_BLEND)


# Here is one thing we do different. We pass it our own surface that we want it
# to use. This way, it won't set the display.
gui.init(*viewport)

app = gui.App(width=640, height=480)

w1 = gui.Button("reset", x=20, y=30)
w2 = gui.Input(x=100, y=30, width=240)

app.add(w1,w2)


def callback():
    w2.value = "GooeyPy is cool!"
w1.connect(CLICK, callback)

mon = gui.Switch(False, labels=("Multiple", "Single"), x=430, y=200, min_width=110)
app.add(mon)
don = gui.Switch(False, labels=("Disabled", "Enabled"), x=430, y=260, min_width=110)
app.add(don)

sb1 = gui.SelectBox(disabled=don.link("value"), multiple=mon.link("value"),
        x=200, y=200, width=200, height=100, scrollable=True)
sb1.add("Value 1", "value1")
sb1.add("Value 2", "value2")
sb1.add("Value 3", "value3")
sb1.add(w2, "inputvalue")

app.add(sb1)


while True:
    clock.tick(40)

    events = pygame.event.get()

    for event in events:
        if event.type == QUIT:
            sys.exit()

    app.run(events)
    glClear(GL_COLOR_BUFFER_BIT)
    app.draw()
    pygame.display.flip()