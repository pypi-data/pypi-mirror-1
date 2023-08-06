#!/usr/bin/env python
# encoding: utf-8

from textrpg import Char, story, ask, give_exp
from save import save

name = ask("What's your name?")

# First load the chars for better gameflow. 
char2 = Char(source="tag:1w6.org,2008:Nasfar")
char1 = Char(source="tag:1w6.org,2008:" + name)

story('''
Where the sun doesn't shine, 
and the stars flicker and wane, 
and terror reigns over the land, 
a hero is born to save us. 

Or not.
''')

char2.say("""I don't know about life or death or anything. I only know I want to live. 

I don't know about heroes, they come and go, but I persist, and I follow them when they move across the lands. 

Don't hope for the heroes. They will desert you when you need them most, because heroes live to die. 

But I live to live, so don't hope for my help, either. 

Please don't hope for my help.
""")


char1.say("""You're a wimp!
I'll show you "don't hope for my help"!

It's time to die!
""")


won = char1.battle(char2)

if won:
    char1.say("So much for 'you survive'!")
    give_exp(char1, 1)
else:
    char2.say("Harr! You won't be the one to kill me!")

story("""And thus ends another battle on the plains of darkness.
""")

story(char1.name + " reached " + str(char1.exp) + " points of experience during these battles.")

if char1.exp >= 13: 
    story("""
which means you won at least 9 concurrent battles! Congratulations!""")
    if not won: 
        story("You can be sure that you'll get a place in the ranks of the best fighters of this place.")

save([char1, char2])
