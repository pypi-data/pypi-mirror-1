#!/usr/bin/env python
# encoding: utf-8

"""PygameRPGs - Play your textrpg stories with grphics.

"""
# first try using pygame, since I'm at my XO right now.
import pygame
from pygame.locals import * # things like event types
import sys # stuff about the program, like quitting it. 
# Threading
from threading import Thread
from time import sleep

class GameThread(Thread): 
    def __init__(self, *args, **kwds): 
        super(GameThread, self).__init__(*args, **kwds)
        pygame.init()
        pygame.display.init()
        self.size = width, height = 1200, 900
        self.screen = pygame.display.set_mode(self.size)
        
    def run(self): 
        while True: 

            fungus_update(stuff)
            fungus_handle_events()
            # show it for some time. 
            sleep(0.1)
    def loop(self): 
        while 1: 
            sleep(0.1)
            

game = GameThread()
size = game.size
screen = game.screen

# We want to display a level: That's simply a list of tiles. 
# For convenient level creation we show it as a list of letters. 
# This is for still level parts. 

# to make this cleaner and the game look nicer, this init of objects should make 
# (obj, objRect) tile tuples

o = 'o' # clear
t = 't' # tree
g = 'g' # ground
r = 'r' # road

level = [
[o, o, o], 
[t, r, g], 
[g, r, g], 
[g, g, g]
]

font_size = min(size[0]/len(level[0]), size[1]/len(level)) # min(x, y)


# TODO: fungus_tile() -> optionally animated tiles. 
def fungus_text(txt, coords = (0,0), size = font_size, color = (10, 10, 10)): 
   """Easily create text objects.

@return: (text, textRect) for direct blitting"""
   # pygame is quite complicated, here. 
   # First a font object
   font = pygame.font.Font(None, size)
   # then the text with color
   text = font.render(txt, True, color)
   # and its surrounding rect
   textRect = text.get_rect()
   # with coords, centered
   textRect.left = coords[0] - textRect.width / 2.0
   textRect.top = coords[1] - textRect.height / 2.0
   
   return text, textRect

def fungus_update(stuff, background_color = (240, 240, 240)): 
   """Show all stuff. 

@param stuff: a list of (object, objectRect) for blitting."""
   # first add the background color
   screen.fill(background_color)
   # then blit all stuff. 
   for i in stuff: 
      screen.blit(i[0], i[1])
   # and show it
   pygame.display.flip()


stuff = []

step = (size[0] / len(level[0]), size[1] / len(level))

#for y in range(len(level)): 
#   for x in range(len(level[y])): 
#      text, textRect = fungus_text(level[y][x], coords = ((x + 0.5)*step[0], (y + 0.5)*step[1]))
#      stuff.append((text, textRect))

# create the main text

txt = ""
text, textRect = fungus_text(txt)

# add an actor, which should be controllable with the keyboard.
#actor, actorRect = fungus_text("I", coords = (0, 0))
#actorRect.left += 0.5 * step[0]
#actorRect.top += 0.5 * step[1]
#stuff.append((actor, actorRect))

def fungus_handle_events(): 
   """Handle all kinds of events. 

One example is the event to quit the program, others are keys...
"""
   for event in pygame.event.get():
      # pygame quit or escape
      if event.type == QUIT or event.type == KEYDOWN and event.key == K_ESCAPE: 
         sys.exit()
      # Movement of the main actor
#      elif event.type == KEYDOWN: 
#         if event.key == K_UP: 
#            actorRect.top -= step[1] # step y
#         elif event.key == K_DOWN: 
#            actorRect.top += step[1] # step y
#         elif event.key == K_LEFT: 
#            actorRect.left -= step[0] # step x
#         elif event.key == K_RIGHT: 
#            actorRect.left += step[0] # step x
#         print (actorRect.left, actorRect.top)



game.start()

print "test"
txt = "test"
