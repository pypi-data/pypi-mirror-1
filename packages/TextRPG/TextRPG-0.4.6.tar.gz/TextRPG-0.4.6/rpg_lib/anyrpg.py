#!/usr/bin/env python
# encoding: utf-8

"""AnyRPG - Basic functions and classes for simple RPG scripting modules.

It contains the basic functions any RPG scripting module which wants to be compatible with TextRPG stories needs to provide. 

TODO: Add doctests, since it begins to become more complex... 

Plans: 
    - Simple to use functions in easy to read scriptfiles in the style of the ministory file. 
    - char.compete(other, skill_name) -> See who wins and by how much. 

Ideas: 
    - Lazy loading modules, to be able to print stuff at once without having to print before the imports. 
    - Add getting experience for groups and show the chars together (only one experience header instead of one per char). 
    - Being able to press "pause" when using autoscrolling output. 


Basic design principles for the scripting language: 
    
    - The action is character centered wherever possible and useful. 
       -> char.say(text) instead of dialog(char, text)
    
    - Anything which affects only one character or any interaction between only a few characters which is initiated by one of them gets called from the character via char.action(). 
       -> char.compete_skill(char2, skill_name) instead of competition_skill(char1, char2, skill_name)
    
    - Anything which affects the whole scene, or a whole group of not necessarily interacting characters gets called as basic function via action() or as class in its own right via class.action(). 
       -> save([char1, char2]) instead of char1.save() char2.save()
    
    - The seperate class way should only be chosen, if the class can feel like a character in its own right and needs seperate states which may or may not be persistent over subsequent runs. 
       -> For example AI.choose_the_way(players_answer) or music.action()
    
    - Data should be stored inside the chars wherever possible. If a script gets started with the same character again, the situation should resemble the previous one as much as possible, except where dictated otherwise by the story. 
       -> char.save() instead of 'on quit' store_char_data(char) + 'on start' load_char_data(char)
    
    - Actions should be written as verb_noun or simply verb. 
       -> char.say() and char.compete_skill() instead of char.text() and char.skill_compete()
     
    - In the story function, an action is a parameter of the story. 
       -> story(switch_background_image="bg_image.png")
     

Design:
    - revert: story() is a function, but should be heavily overloaded, so it gets 
used for any kind of interacion with the setting. -> story(background="...", 
show_image="...", clear_images=True, background_musi="...", play_sound="...", ...)
      Reason: The story is the central background. 
      It creates the setting, just like an exposition. 
      So it can be treated in a special way. 
      This means: Doing it this way makes the scripts appear more natural (to me). 
      Also this allows story() to rearrange the order of passed arguments, if all get passed in one step -> a simpler way to say "new scene". 


This (and other) code can be found at U{http://freehg.org/ArneBab/textrpg}

Doctests: 
    >>> story_helper = Story()
    >>> story_helper.story("The flow changes", autoscroll=True)
    The flow changes
    >>> story_helper.story("", autoscroll=True)
    <BLANKLINE>

"""

# Structure for the metadata inspired by Fufezan: 
# -> http://fufezan.net/python.php
__copyright__ = """ 
  TextRPG - Simple TextRPG module built on top of the 1d6 RPG library.
  -> http://freehg.org/ArneBab/textrpg
----------------------------------------------------------------- 
© 2008 - 2008 Copyright by Arne Babenhauserheide(arne_bab@web.de) 

  This program is free software; you can redistribute it and/or modify
  it under the terms of the GNU General Public License as published by
  the Free Software Foundation; either version 3 of the License, or
  (at your option) any later version.

  This program is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU General Public License for more details.

  You should have received a copy of the GNU General Public License
  along with this program; if not, write to the Free Software
  Foundation, Inc., 51 Franklin St, Fifth Floor, Boston,
  MA 02110-1301 USA

""" 
__author__    = 'Arne Babenhauserheide' 
# __date__      = '7th March 2007' 
__url__       = 'http://rpg-1d6.sf.net' 

__version__   = '0.1' 

import sys
from textrpg_1d6 import Char as ews_char
from time import sleep # for autoscrolling

### Classes ###

class UserInteraction(object): 
    """Basic user interaction: Showing and asking things."""
    def __init__(self, *args, **kwds): 
	self.line_length = 80 #: The maximum length of story lines. 
	self.line_wait = 0.4
	self.char_wait = 0.05
        super(UserInteraction, self).__init__(*args, **kwds)
	
        
    def ask(self, question=None, *args, **kwds): 
        """Ask a question.
        
        Note: Not console based implementations will want to overwrite this. 
	
	Plans: 
		- ask(question=None, default=0, *answers, **kwds) - usage: ask("why", "because", "it's how it is", "I don't know", default=2) -> default capitalized, rest small print. 
	"""
        if question is not None: 
	    sleep(0.01)
            return raw_input(_(question) + " ")

    def split_diag(self, text, line_length = None, localize=True, autoscroll=False, line_beginning = "", *args, **kwds): 
	"""Print a dialog in single lines split at word borders. 
	
	@param text: The text to output. 
	@param line_length: Maximum length of a line. 
	
	"""
	# Split the text by words to output at most self.line_length chars per line. 
	if line_length is None: 
	    line_length = self.line_length
	text_to_print = ""
	# Preserve leading spaces. 
	if text: 
	    while text[0] == " ": 
		text_to_print += " "
		text = text[1:]
	# Print as many words as possible without breaking the max line width. 
	for j in text.split(): 
	    if len(line_beginning) + len(text_to_print) + len(j) >= line_length: 
		self.diag(line_beginning + text_to_print, localize=localize, autoscroll=autoscroll, *args, **kwds)
		# If j > self.line_length -> split j and use only the remaining rest as default, printing all else directly. 
		if len(line_beginning) + len(j) > self.line_length: 
		    while j[self.line_length - len(line_beginning):]: 
			self.diag(line_beginning + j[:self.line_length - len(line_beginning)], localize=localize, autoscroll=autoscroll, *args, **kwds)
			j = j[self.line_length - len(line_beginning):]
		text_to_print = j
	    else: 
		# if we already have text_to_print, add j with a space. 
		if text_to_print: 
		    text_to_print += " " + j
		else: 
		    text_to_print = j
	# Print the last line of this dialog. 
	self.diag(line_beginning + text_to_print, localize=localize, autoscroll=autoscroll, *args, **kwds)
    
    def diag(self, data, localize=True, autoscroll=False, line_wait = None, char_wait = None, relative_speed = 1, end_with_linebreak = True, position_in_line = 0, *args, **kwds):
	""" Print a dialog line. 
	
	@param line_wait: The time to wait at linebreaks before continuing with the text. 
	@param char_wait: The time to wait per char before printing the next char. 
	@param relative_speed: The relative speed of this dialog compared to others. - Limitation: Speed can only be adjusted for whole lines! 
	@param autoscroll: If diag should output char by char (True) or wait for user input for each lines (False). 
	@param end_with_linebreak: If there should be a linebreak at the end (True), or if the next dialog should write on the same line (False). 
	@param position_in_line: Where in the text line the cursor should be positioned when writing. 
	"""
	# If the method doesn't get line_wait and/or char_wait, it uses the default values for the UI. 
	# With this we can customize the speed of the output. 
	if line_wait is None: 
	    line_wait = self.line_wait
	if char_wait is None: 
	    char_wait = self.char_wait

	# Now adjust the speed by the relative speed: 
	if relative_speed != 1: 
	    char_wait *= relative_speed
	    line_wait *= relative_speed

	# Localize the text
        if localize: 
            text = _(data)
        else: text = data 
    
	# And output it. 
	# If we have no autoscrolling, we just output the text. 
        if not autoscroll: 
            raw_input(text)
	
	# If we have autoscrolling, we print it char by char. 
	# Limitation: This looks really dumb, if the text is longer than one line. 
        else: 
	    if text: 
		sys.stdout.write('\033[' + str(position_in_line) + 'G')
                sys.stdout.flush()
	    else: 
		self.diag("...press enter to read on...") # press enter to read on at each empty line, so readers can rest. 
                # clear the line after the user pressed enter.
                sys.stdout.write('\033[2A\033[' + str(position_in_line) + 'G')
		for i in range(len(_("...press enter to read on..."))): 
		    sys.stdout.write(" ")
                sys.stdout.flush()
		#sleep(line_wait)
            # First sleep 1/10th second. This ensures that the text gets shown before sleeping.
            sleep(char_wait)
	    # If we have text, wait one 10th of a second per char. 
	    for i in text: 
		# load the current cursor position
		sys.stdout.write(i)
                sys.stdout.flush()
		sleep(char_wait)
	
	# If we want a linebreak at the end, add it. 
	if end_with_linebreak: 
	    # Move back after the last char on the last line. 
	    sys.stdout.write("\n")
            sys.stdout.flush()

class Dialogs(object): 
    """Basic dialogs. 
    
    A dialog never interacts with the user directly, it just provides template for otehr code.
    
    If you want a specific interaction, write a function in UserInteraction, or split the dialog and interact via the higher classes (i.e. Char or Story)."""
    def __init__(self, *args, **kwds): 
        super(Dialogs, self).__init__(*args, **kwds)
    
    def get_experience(self, chars, amount=0):
        """Show the experience the chars get and what they do with it."""
        text = ""
        print self.get_experience_header(chars=chars, amount=amount)
            
        # Info text for each char. 
        for i in chars: 
            result = i.incremental_upgrade(amount=1)
            if result: 
                text += result 
            
        # Dialog footer. 
        text += self.get_experience_footer(chars, amount=amount)
        return text
    
    def get_experience_header(self, chars, amount=0):
        """@return: The header line of the experience dialog."""
        scribble = ""
        if len(chars) == 1: 
            scribble += "\n***experience of " + chars[0].name + "***\n"
            scribble += chars[0].name + " got " + str(amount) + " experience."
        else: 
            scribble += "\n***experience***\n"
            scribble += "The characters got " + str(amount) + " experience."
        return scribble
    
    def get_experience_footer(self, chars, amount=0):
        """@return: The header line of the experience dialog."""
        return "***/experience***\n"
    
    
    def upgrade_info(self, char, amount): 
        """Return the effects of improving the char by the given amount of points/Strichen."""
        upgrade = char.upgrade(amount)
        item_name = " ".join(upgrade[0].items()[0][0])
        old_value = upgrade[0].items()[0][1]["Zahlenwert"] 
        new_value = upgrade[1].items()[0][1]["Zahlenwert"]
        if old_value < new_value:
            return char.name + " raised " + item_name + " from " + str(old_value) + " to " + str(new_value) + "\n"
        else: 
            return False


class Char(ews_char, UserInteraction, Dialogs):
    """A Char is any character in the game, those from the player as well as others."""
    def __init__(self, template=False, *args, **kwds): 
        """A Char is any character in the game, those from the player as well as others."""
        super(Char, self).__init__(template=template, *args, **kwds)
        self.battle_diff_treshold = 4 #: The treshold of the char below which no hit is scored. 
    
    def say(self, data, *args, **kwds): 
        """Say something -> Show that the char says it."""
        data = _(data)
        for i in data.split("\n"): 
            self.split_diag(i, localize=False, line_beginning = self.name + ': ', *args, **kwds)
    
    def ask(self, data, localize=False, *args, **kwds): 
        """Say something -> Show that the char says it."""
        data = _(data)
        for i in data.split("\n")[:-1]: 
            self.diag(self.name + ': ' + i, localize=localize, *args, **kwds)
        return super(Char, self).ask(self.name + ': ' + data.split("\n")[-1], *args, **kwds)
    
    def act(self, data, *args, **kwds): 
        """Do something -> Show that the char does it in the style "<name> walks away.".
        
        Usage: 
            >>> char = Char(source="tag:1w6.org,2008:Mins")
            >>> char.act("walks away.")
            Mins walks away.
        """
        data = _(data)
        for i in data.split("\n"): 
            self.diag(self.name + ' ' + i, localize=False, *args, **kwds)
        
    def compete_skill(self, other, skill_name, self_mods=[], other_mods=[]): 
        """Compete with the other char in the specified skill. 
        
        @return If we won and by how much: (won, diff). Diff is always >=0. 
        """
        my_result = self.roll(self.get_effective_skill_value(skill_name, related_skills=[], related_attributes=[]), mods=self_mods)
        other_result = other.roll(other.get_effective_skill_value(skill_name, related_skills=[], related_attributes=[]), mods=other_mods)
        return my_result > other_result, abs(my_result - other_result)
    
    def get_exp(self, amount=0): 
        """Get experience and show it."""
        for i in self.get_experience([self], amount).splitlines(): 
            self.diag(i)
    
    def incremental_upgrade(self, amount=0): 
        # Upgrade in single point steps, so the experience gets spread a bit. 
        # if it's less than two points, use it completely. 
        if amount <= 2: 
            text = self.upgrade_info(self, amount)
        # If it's more than one point, spread all but one in single points 
        # and at last improve by 1 plus the remaining fraction. 
        # With this, no value gets less than one point/Strich 
        # (no use in spreading points which can only give an increase by pure chance). 
        else: 
            text = ""
            for j in range(int(amount) -1): 
                text += self.upgrade_info(self, 1)
            text += self.upgrade_info(self, amount - int(amount) + 1)
        return text
    
    def battle(self, other): 
        """Fight a deadly battle."""
        return self.fight_while_standing(self, other)
    
    def fight_while_standing(self, me, other):
        '''Fight as long as both characters are still active.
        
        Plans: 
            - TODO: Select fight styles, when you attack as well as when the other attacks. 
        '''
        
        # Show the battle status of both chars. 
        self.diag(self.battle_info(me, other))
        
        # Ask the player which action to take.        
        self.diag(other.name + ' comes closer.')
        won, injuries_self, injuries_other = self.select_battle_action(me, other)
        
        self.diag(self.battle_round_result(me, other, won, injuries_self, injuries_other))
        
        self.diag(self.battle_info(me, other))
        
        while me.active and other.active:
            if won: # we won the last round, so we can attack again.
                won, injuries_self, injuries_other = self.select_battle_action(me, other)
            else: 
                self.diag(other.name + " attacks you.")
                won, injuries_self, injuries_other = self.select_battle_style(me, other, attacker=False)
            
            self.diag(self.battle_round_result(me, other, won, injuries_self, injuries_other))
            
            self.diag(self.battle_info(me, other))
        
        if me.active: 
            return True # We won
        else: 
            return False # We lost
    
    def battle_info(self, me, other): 
        """Status information about a battle.
        
        @return: Completely formatted String to display. """
        return "\n" + me.battle_stats() + "\n\n" + other.battle_stats() + "\n"
    
    def battle_round_result(self, me, other, won, injuries_self, injuries_other): 
        """Return the result of one round of battle. Called with the battle results (won, injuries_self, injuries_other)."""
        if won: 
            scribble = _("\nYou won this round.")
            if injuries_other[2] != 0: 
                scribble += "\n" + other.name + _(" took ") + str(injuries_other[2]) + _(" points of damage")
                if injuries_other[0] == 1: 
                    scribble += _(" and a deep wound.") # You never get more than one wound per enemy in one round in the 1d6 rpg. 
                elif injuries_other[1] == 1: 
                    scribble += _(" and a critical wound.") # You never get more than one wound per enemy in one round in the 1d6 rpg. 
                else: scribble += "."
        else: 
            scribble = _("\nYou didn't win this round.")
            if injuries_self[2] != 0: 
                scribble += "\n" + _("and you took ") + str(injuries_self[2]) + _(" points of damage")
                if injuries_self[0] == 1: 
                    scribble += _(" and a deep wound.") # You never get more than one wound per enemy in one round in the 1d6 rpg. 
                elif injuries_self[1] == 1: 
                    scribble += _(" and a critical wound.") # You never get more than one wound per enemy in one round in the 1d6 rpg. 
                else: scribble += "."
        return scribble
    
    def select_battle_action(self, me, other, attack=True): 
        """Ask which action to take in the battle.
        
        @param me: The player char. 
        @type me: Char
        @param other: The enemy. 
        @type other: Char
        
        @param attack: Whether the character is the attacker. 
        @type attack: True/False
        
        @return: The result of the battle (won or lost, wounds)."""
        
        if self.ask('Do you want to attack ' + other.name + '? (Yes, no) ').lower() in ['yes', 'y', '']: 
            self.diag("You attack " + other.name + ".")
            won, injuries_self, injuries_other = self.select_battle_style(me, other, attacker=True)
        else:
            self.diag("You don't attack, so you could do something else this round, if this was already implemented.")
            won, injuries_self, injuries_other = False, [0, 0, 0], [0, 0, 0]
        return won, injuries_self, injuries_other 
        
    def select_battle_style(self, me, other, attacker): 
        """Select how to fight.
        @param attacker: Is me the attacker? 
        @type: Bool
        """
        styles_self = []
        style = self.ask("How do you want to fight? (Usual, defensive, target head)")
        if style.lower() in ["target head", "head", "h"]: 
            styles_self.append("target head")
        elif style.lower() in ["defensive", "d"]: 
            styles_self.append("defensive")
        # TODO: Use the style. 
        if attacker: 
            won, injuries_self, injuries_other = me.fight_round(other, styles_self=styles_self)
        else: 
            won, injuries_other, injuries_self = other.fight_round(me, styles_other=styles_self)
            won = not won
        return won, injuries_self, injuries_other
    
    def battle_stats(self):
        """@return: A string with battle status information, formatted as battle stats"""
        scrib = _("---battle-stats for ") + _(self.name) + _("---")
        scrib += _('\nLife: ') + str(self.TP) + _(" of ") + str(self.bTP)
        scrib += _('\nWounds: ') + str(self.wounds[0]) + _(" - crippling wounds: ") + str(self.wounds[1])
        scrib += _("\nSkill: ") + str(self.attack)
        scrib += _("\nWeapon: ") + str(self.weapon)
        scrib += _("\nArmor: ") + str(self.armor)
        scrib += _("\n---/battle-stats---")
        return scrib
    
    def fight_round(self,  other, styles_self=[], styles_other=[]):
        """One battle action against another char.
        
    @param styles_self: The different styles the char should use (defense, pull back, escape, target: area). 
    @type styles_self: A list of Strings. 
    
    @param styles_other: The different styles the enemy uses. 
    @type styles_other: A list of Strings. 
    
    @return: [ If the char won (bool), [your new wounds, critical, taken tp damage], [the 
enemies new wounds, critical, taken tp damage] ]

    Plans: 
        - TODO: Add options for own fight style. 
        - TODO: Add options for other fight style. 
        
    Planned options for own fight style: 
        - defense (+6, no damage enemy)
        - pull back (+9, no damage enemy)
        - try to escape. 
        - target specific body area for additional damage. 
        - Shield/evasion (treshold for the enemies diff, below which no hit was archieved).
    
    Ideas: 
        - Define a damage multiplier, which shows how effective the damage type is against the specific enemy -> do that in the char itself. 
        - Define the effectivity of the armor against the weapon. 
        - Get the treshold directly from the char. 
."""
       # Initialize all variables empty
        won = None #: Did we win this round?
        mods_self = [] #: The modifiers for the protagonists attack roll. 
        mods_other = [] #: The modifiers for the enemies attack roll. 
        deep_wounds_self, deep_wounds_other, critical_wounds_self, critical_wounds_other = 0, 0, 0, 0
        
        
        # Apply the effects of the fighting styles. 
            # For the attacker
        # The defensive style gives 6 points bonus, but the other char won't take any damage. 
        if "defensive" in styles_self: 
            mods_self.append(+6)
        # Targetting the head gives 6 points malus, but increases the damage by 18 points. 
        if "target head" in styles_self: 
            mods_self.append(-6)
            
            # For the defender
        # The defensive style gives 6 points bonus, but the other char won't take any damage. 
        if "defensive" in styles_other: 
            mods_other.append(+6)
        # Targetting the head gives 6 points malus, but increases the damage by 18 points. 
        if "target head" in styles_other: 
            mods_other.append(-6)
        
        
        #: The damage we get
        self.damage_self = 0
        #: The damage the other gets
        self.damage_other = 0
        
        # Do the rolls for both fighters. 
        attack_self = self.attack_roll(mods=mods_self)
        attack_other = other.attack_roll(mods=mods_other)
        
        # If I throw higher
        if attack_self > attack_other: 
            won = True
            if not "defensive" in styles_self: 
                # Now check for damage (we hit)
                # The damage consists of several factors. 
                # First the difference between the attack rolls. 
                self.damage_other += attack_self - attack_other
                # Then the damage of our weapon. 
                self.damage_other += self.dam
                # And substracted the armor of the other. 
                self.damage_other -= other.arm
                
                # For specific body ares, the damage increases. 
                if "target head" in styles_self: 
                    self.damage_other += 18
        
                # Clean out negative damage. If the damage is below zero, the armor caught all damage. 
                if self.damage_other < 0: 
                    self.damage_other = 0
                
                # Now actually do the damage. This returns a tuple: (new deep wounds, new critical wounds)
                deep_wounds_other, critical_wounds_other = other.damage(tp=self.damage_other)
        
        # If the other rolls better
        elif attack_self < attack_other: 
            won = False
            # Check for our damage (the other hit)
            if not "defensive" in styles_other: 
                # The damage consists of several factors. 
                # First the difference between the attack rolls. 
                self.damage_self += attack_other - attack_self
                # Then the damage of our weapon. 
                self.damage_self += other.dam
                # And substracted the armor of the other. 
                self.damage_self -= self.arm
                
                # For specific body ares, the damage increases. 
                if "target head" in styles_other: 
                    self.damage_self += 18
    
                # Clean out negative damage. If the damage is below zero, the armor caught all damage. 
                if self.damage_self < 0: 
                    self.damage_self = 0
                
                # Now actually take the damage. This returns a tuple: (new deep wounds, new critical wounds)
                deep_wounds_self, critical_wounds_self = self.damage(tp=self.damage_self)

        # If we get the same result, the attacker wins, us. 
        else:   
            won = True
            if not "defensive" in styles_self: 
                # Now check for damage (we hit)
                # The damage consists of several factors. 
                # First the difference between the attack rolls. 
                self.damage_other += attack_self - attack_other
                # Then the damage of our weapon. 
                self.damage_other += self.dam
                # And substracted the armor of the other. 
                self.damage_other -= other.arm
                
                # For specific body ares, the damage increases. 
                if "target head" in styles_self: 
                    self.damage_other += 18
            
                # Clean out negative damage. If the damage is below zero, the armor caught all damage. 
                if self.damage_other < 0: 
                    self.damage_other = 0
                
                # Now actually do the damage. This returns a tuple: (new deep wounds, new critical wounds)
                deep_wounds_other, critical_wounds_other = other.damage(tp=self.damage_other)
            
        return won, [deep_wounds_self, critical_wounds_self, self.damage_self], [deep_wounds_other, critical_wounds_other, self.damage_other]
    

class Story(UserInteraction, Dialogs): 
    """The main component for telling stories. Subclass this to change all behaviour."""
    def __init__(self, *args, **kwds): 
        """The main component for telling stories."""
        super(Story, self).__init__(*args, **kwds)
    
    def story(self, data=None, *args, **kwds):
        """Tell a part of the story."""
        if data is not None: 
            data = _(data)
            for i in data.split("\n"): 
                self.diag(i, localize=False, *args, **kwds)
    
    def save(self, chars=[], *args, **kwds):
            """Save the current state."""
            for i in chars:
                    i.save()
    
    def give_exp(self, char, amount=0, *args, **kwds): 
        """Give experience to only one char."""
        for i in self.get_experience([char], amount=amount).splitlines(): 
            self.diag(i)


class MissingScriptingFunction(Exception): 
    """A warning to display if any necessary scripting function isn't implemented."""
    def __init__(self, func, implementation = None): 
        self.func = func
        self.implementation = implementation
        pass
    def __str__(self): 
        if self.implementation is None: 
            return "The function " + str(self.func) + " must be implemented by every rpg scripting module to allow for easy changing of function behaviour."
        else: 
            return "The function " + str(self.func) + " must be implemented by every rpg scripting module to allow for easy changing of function behaviour." \
                    + "\nThe simplest way is to just add the following lines to your script: " \
                    + "\n\nstory_helper = Story()\n" \
                    + self.implementation
        

### Functions ###

de_DE = {
#"""...press enter to read on...""": """...zum weiterlesen Enter drücken...""",
}

def _(text, locale="en_EN", locales={"de_DE": de_DE}):
    '''String function to allow localizing later on. 
    
    @return: A localized string. '''
    # TODO: Localize cleanly - this is but a test. 
    if text in locales["de_DE"]: 
	return locales["de_DE"][text]
    else: 
	return str(text)



## Functions needed to be implemented in EVERY simple rpg scripting module (changing their effect for all places where they get used can only be done in the Story class) ###
def ask(question, *args, **kwds): 
    raise MissingScriptingFunction(ask, implementation = """def ask(question, *args, **kwds): 
    return story_helper.ask(question, *args, **kwds)""")
    
def diag(text, localize=True, autoscroll=False, *args, **kwds): 
    raise MissingScriptingFunction(ask, implementation = """def diag(text, localize=True, autoscroll=False, *args, **kwds): 
    return story_helper.diag(text, localize=localize, autoscroll=autoscroll, *args, **kwds)""")

def story(text=None, *args, **kwds): 
    raise MissingScriptingFunction(ask, implementation = """def story(text=None, *args, **kwds): 
    return story_helper.story(text, *args, **kwds)""")

def give_exp(char, amount, *args, **kwds): 
    raise MissingScriptingFunction(ask, implementation = """def give_exp(char, amount, *args, **kwds): 
    return story_helper.give_exp(char, amount, *args, **kwds)""")

def save(chars=[], *args, **kwds): 
    raise MissingScriptingFunction(ask, implementation = """def save(chars=[], *args, **kwds): 
    return story_helper.save(chars=chars, *args, **kwds)""")

def battle(me, other, *args, **kwds): 
    raise MissingScriptingFunction(ask, implementation = """def battle(me, other, *args, **kwds): 
    return me.battle(other, *args, **kwds)""")



### Self-Test ###

def _test(): 
    """Do all doctests."""
    from doctest import testmod
    testmod()

if __name__ == "__main__": 
    _test()
