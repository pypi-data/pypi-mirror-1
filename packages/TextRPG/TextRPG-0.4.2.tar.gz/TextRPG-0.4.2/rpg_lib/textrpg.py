#!/usr/bin/env python
# encoding: utf-8

"""TextRPG - Simple TextRPG module built on top of the 1d6 RPG library.

Usage: 
    - ministory_helper.py 
    Test the ministory (a testcase for the textrpg module)
    - textrpg.py 
    Start the internal test story of the textrpg. 

Plans: 
    - put all functions which need diag or ask or similar into a class, 
      so diag and ask can be overridden by other modules (doesnt work right now). 
    - Simple to use functions in easy to read scriptfiles in the style of the ministory file. 
    - char.compete(other, skill_name) -> See who wins and by how much. 
    - a basic implementation as minimal api reference for anyrpg plugins.
    - Show the text letter by letter, if that's possible. 
    - Add the basic scripting function "python_interpreter(startup_data)", which shows an interactive python interpreter with the startup data already entered and interpreted. 


Ideas: 
    - Lazy loading modules, to be able to print stuff at once without having to print before the imports.
    - Add getting experience for groups and show the chars together (only one experience header instead of one per char). 


Basic design principles for the scripting language: 
    
    - The action is character centered wherever possible and useful. 
       -> char.say(text) instead of dialog(char, text)
    
    - Anything which affects only one character or any interaction between only a few characters which is initiated by one of them gets called from the character via char.action(). 
       -> char.compete_skill(char2, skill_name) instead of competition_skill(char1, char2, skill_name)
    
    - Anything which affects the whole scene, or a whole group of not necessarily interacting characters gets called as basic function via action() or as class in its own right via class.action(). 
       -> save([char1, char2]) instead of char1.save() char2.save()
    
    - The seperate class way should only be chosen, if the class can feel like a character in its own right and needs seperate states which may or may not be persistent over subsequent runs. 
       -> For example AI.choose_the_way(players_answer) or music.action()
    
    - Data should be stored inside the chars wherever possible. If a script gets started with the same character again, the situation should resemble the previous one as much as possible, except where dictated otherwise by the story_helper. 
       -> char.save() instead of 'on quit' store_char_data(char) + 'on start' load_char_data(char)
    
    - Actions should be written as verb_noun or simply verb. 
       -> char.say() and char.compete_skill() instead of char.text() and char.skill_compete()
    
    - In the story function, an action is a parameter of the story. 
       -> story(switch_background_image="bg_image.png")

The code for the TextRPG can be found at U{http://dreehg.org/ArneBab/textrpg}

"""

try: 
    from anyrpg import __copyright__, __url__, __author__
except: 
    from rpg_lib.anyrpg import __copyright__, __url__, __author__

__version__   = '0.4.2' 
# __date__      = '7th March 2007' 


print "...Loading rpg library..."


try: 
    # AnyRPG classes
    from anyrpg import Char
    from anyrpg import Story as any_story
    # AnyRPG function for localizing. 
    from anyrpg import _
except: 
    # AnyRPG classes
    from rpg_lib.anyrpg import Char
    from rpg_lib.anyrpg import Story as any_story
    # AnyRPG function for localizing. 
    from rpg_lib.anyrpg import _


# Changing things. I want to display "..." in front of every blank story line. 

class Story(any_story): 
    def __init__(self, *args, **kwds): 
        super(Story, self).__init__(*args, **kwds)
    
    def story(self, data=None, *args, **kwds): 
        """Tell a part of the story.
        
        Overridden to show "..." instead of blank lines (override commented out). """
        if data is not None: 
            data = _(data)
            for i in data.split("\n"): 
                #if i.rstrip() == "": 
                #    self.diag("...", localize=False)
                #else: 
                    self.diag(i, localize=False)
        

# Define helper functions. 
story_helper = Story()

### Lines needed in EVERY simple rpg scripting module (changing their effect for all places where they get used can only be done in the Story class) ###
def ask(question, *args, **kwds): 
    return story_helper.ask(question, *args, **kwds)

def diag(text, localize=True, autoscroll=False, *args, **kwds): 
    return story_helper.diag(text, localize=localize, autoscroll=autoscroll, *args, **kwds)

def story(text=None, *args, **kwds): 
    return story_helper.story(text, *args, **kwds)

def give_exp(char, amount, *args, **kwds): 
    return story_helper.give_exp(char, amount, *args, **kwds)

def save(chars=[], *args, **kwds): 
    return story_helper.save(chars=chars, *args, **kwds)

def battle(me, other, *args, **kwds): 
    return me.battle(other, *args, **kwds)


### Test story lines ###

def greet(char): 
    diag("Old man: Welcome traveller. You've come to the right place to learn about your heritage.")
    diag("Sadly you aren' well liked around here.")
    diag("Heges for example didn't like your father too much.")
    diag("Oh well, that was an understatment. You should better prepare yourself to face him. I think he'd love to see your face in the mud. Here's my knife. I like fights to be fair.")
    diag("...")
    diag("You say you don't know who we think you are?")
    diag("Well, at least tell me your name then, and I'll tell you a bit about your father, after you won.")
    char.name = raw_input("My Name: ")
    diag("You've got a nice name, " + char.name + ". Good luck!")


if __name__ == "__main__": 
    print "...Creating main character..."
    char = Char()
    greet(char)
    print "...Creating enemy character..."
    choss = Char(source='tag:1w6.org,2008:Hegen')
    choss.name = "Hegen"
    won = battle(char, choss)
    if won: 
        diag(char.name + " won the fight.")
    else: 
        diag(choss.name + " won the fight.")
    give_exp(char, 3)
    choss.upgrade(3)
    if won: 
        diag("Well done " + char.name + ". I knew my trust in you was well placed. Now about your father...")
    else: 
        diag("I didn't expect you to lose to him. Well, fate is a harsh teacher. Better luck next time!")
    
