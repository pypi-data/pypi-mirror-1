#!/usr/bin/env python
# encoding: utf-8

from rpg_lib.textrpg import *

hero = Char() # a generic human :)
peasant = Char(template=True) # A random human with random name. 
enemy = Char() # another generic human :)


story("""Welcome to the world of easy RPG scripting. 

I hope you enjoy your stay!
""")

hero.say("""And welcome from me, too!

I hope we'll be able to go adventuring, soon!

besides: I'm Darjad Merejn.""")

hero.name = "Darjad Merejn"

hero.say("""So now you know my name. Would you tell me yours?""")

name = ask("Your name:")

player = Char(source="tag:1w6.org,2008:" + name)

hero.say("So this time in style: Welcome " + player.name + "!")

enemy.say("""How nice to see you. I hope you enjoy your glee. 

It won't last too long.
""")

hero.say("""How dare you come here! 

I'll splatter your guts, Granash Barn!""")

enemy.name = "Granash Barn"

enemy.say("""Well well, try it!""")

hero.attack = 18 # A quite formidable fighter. 
enemy.attack = 18 # Same goes for him

peasant.attack = 6 # Knows not to grab a dagger from the wrong side. 

peasant.act("tries to get out of the way of " + enemy.name)

story(enemy.name + " attacks " + peasant.name)

won = enemy.fight_round(peasant)[0]
if won: 
   peasant.say("""Aaargh!""")
else: enemy.say("""Damn peasant.""")


hero.say("""How dare you! I'll taste your blood!""")

hero.act("attacks " + enemy.name)

while hero.active and enemy.active: 
   hero.fight_round(enemy)

if hero.active:
   hero.act("won.")
   hero.say("""That's what they call villain these days. 

So now to you. You look kinda sorry for him. 

Seems I'll have to kill you, too.""")
   won = player.battle(hero)
   if not won: 
       story("""And so the adventure of """ + player.name + """ended quite early.""")
else:
   enemy.act("won.")
   enemy.say("""So much for heroes. 

I hope you didn't stand with that bastard. I'm leaving. 

Want to come with me?""")

   join_the_enemy = ask("""Come with him? (Yes, no)""")

   if join_the_enemy.lower() in ["yes", "y", ""]: 
      enemy.say("""A wise decision. Now carry my bag.""")
   else: 
      enemy.say("""That's too bad. Good luck for your future. 

And don't trust the heroes.

Do you want to fight me, then?""")

if player.active: 
   fight = ask("Fight him? (Yes, no)")
else:
   fight = "No"
if fight.lower() in ["yes", "y", ""]:
   won = player.battle(enemy)
   if not won:
      story("Sorry, you lost.")
else:
   enemy.say("""A good fight.""")

exit()
