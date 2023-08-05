"""
In this example, I'm going to show you how easy it is to integrate the gui into
your already made game.
"""

import sys
sys.path.insert(0, "..")

import pygame
import gooeypy as gui
from gooeypy.const import *

clock = pygame.time.Clock()

# Here is our screen that we are already using in our game.
screen = pygame.display.set_mode((640, 480))

# Here is one thing we do different. We pass it our own surface that we want it
# to use. This way, it won't set the display.
gui.init(myscreen=screen)

# We create our app...
app = gui.App()
data = "This example is for demonstrating how you can easily use GooeyPy in your already made game."
tb = gui.TextBlock(value=data, x=100, y=20, width=350)
app.add(tb)

# Lets create a very simple game where you move around an image.
image = gui.get_image("image.png")
x = 200
y = 250
movedir = {
    "right":False,
    "left":False,
    "up":False,
    "down":False,
}

while True:
    clock.tick(40)

    events = pygame.event.get()

    for event in events:
        if event.type == QUIT:
            sys.exit()

        elif event.type == KEYDOWN:
            if event.key == K_RIGHT:
                movedir["right"] = True
            elif event.key == K_LEFT:
                movedir["left"] = True
            elif event.key == K_UP:
                movedir["up"] = True
            elif event.key == K_DOWN:
                movedir["down"] = True

        elif event.type == KEYUP:
            if event.key == K_RIGHT:
                movedir["right"] = False
            elif event.key == K_LEFT:
                movedir["left"] = False
            elif event.key == K_UP:
                movedir["up"] = False
            elif event.key == K_DOWN:
                movedir["down"] = False

    if movedir["right"]:
        x += 5
    if movedir["left"]:
        x -= 5
    if movedir["down"]:
        y += 5
    if movedir["up"]:
        y -= 5
    x = max(0, min(x, 460))
    y = max(100, min(y, 360))

    app.run(events)

    # In the event of wanting the gui to be drawn to the screen every time, you
    # can set "app.dirty = True" before calling app.draw()
    app.draw()

    # With updating the display you have a few options. If you want to flip the
    # entire screen, you can simply do:
    # pygame.display.flip()
    # Or if you are wanting to just update the parts the screen that need to be
    # updated, you can do something like this:

    # In your game, add the rects of the screen that need updating to this list.
    myupdaterects = []

    # Let's use our image that we move around the screen for example.
    dirty_rect = screen.blit(image, (x,y))
    myupdaterects.append(dirty_rect)

    # Now we update the screen!
    myupdaterects.extend(gui.update_rects)
    pygame.display.update(myupdaterects)

    # Don't forget to clear the dirty rect lists!
    myupdaterects = []
    gui.update_rects = []