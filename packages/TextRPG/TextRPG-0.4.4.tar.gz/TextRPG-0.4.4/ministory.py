#!/usr/bin/env python
# encoding: utf-8

from rpg_lib.textrpg import Char, story, ask, give_exp
from rpg_lib.textrpg import save

name = ask("What's your name?")

# First load the chars for better gameflow. 
char2 = Char(source="tag:1w6.org,2008:Nasfar")
char1 = Char(source="tag:1w6.org,2008:" + name)

# won, diff = char1.compete_skill(char2, "cooking")
# won: If we won
# Diff: By how much we won or lost (always positive). 

story("...Press enter to read the next line...")

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
    char1.get_exp(1)
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

#story("""
#So now it's time to prepare the meal for the evening.""")
#
#success = char1.check_skill("cooking")
#if success: 
#    char1.say("At least he won't spoil my meal now.")
#else: 
#    char1.say("Gah! I shouldn't have tried to cook directly after a battle!")

save([char1, char2])
