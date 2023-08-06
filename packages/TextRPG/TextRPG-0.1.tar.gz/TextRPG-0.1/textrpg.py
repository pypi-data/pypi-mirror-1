#!/usr/bin/env python
# encoding: utf-8

"""TextRPG - Simple TextRPG module built on top of the 1d6 RPG library.

Usage: 
    - ministory.py 
    Test the ministory (a testcase for the textrpg module)
    - textrpg.py 
    Start the internal test story of the textrpg. 

TODO: Lazy loading modules, to be able to print stuff at once without having to print before the imports.

Plans: 
    - Simple to use functions in easy to read scriptfiles in the style of the ministory file. 

"""

# Structure for the metadata inspired by Fufezan: 
# -> http://fufezan.net/python.php

__copyright__ = """ 
  rpg-1d6 - A general roleplaying backend. 
  -> http://rpg-1d6.sf.net
----------------------------------------------------------------- 
© Copyright by Arne Babenhauserheide, 2008  (arne_bab@web.de) 

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
__version__   = '0.1' 
__author__    = 'Arne Babenhauserheide' 
# __date__      = '7th March 2007' 
__url__       = 'http://rpg-1d6.sf.net' 


print "...Loading rpg library..."

from textrpg_1d6.char import Char as ews_char

def _(text):
    '''String function to allow localizing later on)'''
    return str(text)

class Char(ews_char):
    def __init__(self, template=False, *args, **kwds): 
        super(Char, self).__init__(template=template, *args, **kwds)
        self.battle_diff_treshold = 4 #: The treshold of the char below which no hit is scored. 
    
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
    def say(self, data): 
        data = _(data)
        for i in data.split("\n"): 
            if i.strip() != "": 
                diag(self.name + ': ' + i, localize=False)
            # If the string is empty, just add a blank line without the characters name. 
            else: diag("...", localize=False)
    
    def fight_round(self, other, *args, **kwds): 
        """Fight for one round."""
        return super(Char, self).fight_round(other, *args, **kwds)
    
    def battle(self, other): 
        """Fight a dadly battle."""
        return battle(self, other)
        
        
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
    

def ask(question): 
    """Ask a question."""
    return raw_input(_(question) + " ")

def story(data):
    data = _(data)
    for i in data.split("\n"): 
        if i.strip() != "": 
            diag(i, localize=False)
        # If the string is empty, just add a blank line without the characters name. 
        else: diag("...", localize=False)
	

def save(chars=[]):
        """Save the current state."""
        for i in chars:
                i.save()

def diag(data, localize=True):
	if localize: 
		raw_input(_(data))
	else: raw_input(data)

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

def battle_info(me, other): 
    """Status information about a battle.
    
    @return: Completely formatted String to display. """
    return "\n" + me.battle_stats() + "\n\n" + other.battle_stats() + "\n"


def battle_round_result(me, other, won, injuries_self, injuries_other): 
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


def select_battle_action(me, other, attack=True): 
    """Ask which action to take in the battle.
    
    @param me: The player char. 
    @type me: Char
    @param other: The enemy. 
    @type other: Char
    
    @param attack: Whether the character is the attacker. 
    @type attack: True/False
    
    @return: The result of the battle (won or lost, wounds)."""
    
    if ask('Do you want to attack ' + other.name + '? (Yes, no) ').lower() in ['Yes', 'y', '']: 
        diag("You attack " + other.name + ".")
        won, injuries_self, injuries_other = select_battle_style(me, other, attacker=True)
    else:
        diag("You don't attack, so you could do something else this round, if this was already implemented.")
        won, injuries_self, injuries_other = False, [0, 0, 0], [0, 0, 0]
    return won, injuries_self, injuries_other 
    

def select_battle_style(me, other, attacker): 
    """Select how to fight.
    @param attacker: Is me the attacker? 
    @type: Bool
    """
    styles_self = []
    style = ask("How do you want to fight? (Usual, defensive, target head)")
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


def battle(me, other): 
    return fight_while_standing(me, other)

def fight_while_standing(me, other):
    '''Fight as long as both characters are still active.
    
    Plans: 
        - TODO: Select fight styles, when you attack as well as when the other attacks. 
    '''
    
    # Show the battle status of both chars. 
    diag(battle_info(me, other))
    
    # Ask the player which action to take.        
    diag(other.name + ' comes closer.')
    won, injuries_self, injuries_other = select_battle_action(me, other)
    
    diag(battle_round_result(me, other, won, injuries_self, injuries_other))
    
    diag(battle_info(me, other))
    
    while me.active and other.active:
        if won: # we won the last round, so we can attack again.
            won, injuries_self, injuries_other = select_battle_action(me, other)
        else: 
            diag(other.name + " attacks you.")
            won, injuries_self, injuries_other = select_battle_style(me, other, attacker=False)
        
        diag(battle_round_result(me, other, won, injuries_self, injuries_other))
        
        diag(battle_info(me, other))
    
    if me.active: 
        return True # We won
    else: 
        return False # We lost

def give_exp(char, amount=9): 
    """Wrapper for scripts."""
    return get_experience(char, amount=amount)

def get_experience(char, amount=0):
    """Show the experience the char gets and what the char does with it."""
    diag("\n***experience of " + char.name + "***")
    diag(char.name + " got " + str(amount) + " experience.")
    upgrade = char.upgrade(amount)
    item_name = " ".join(upgrade[0].items()[0][0])
    old_value = upgrade[0].items()[0][1]["Zahlenwert"] 
    new_value = upgrade[1].items()[0][1]["Zahlenwert"]
    if old_value < new_value:
        diag(char.name + " raised " + item_name + " from " + str(old_value) + " to " + str(new_value))
    diag("***/experience***\n")


if __name__ == "__main__": 
    print "...Creating main character..."
    char = Char()
    greet(char)
    print "...Creating enemy character..."
    choss = Char(source='tag:1w6.org,2008:Hegen')
    choss.name = "Hegen"
    won = fight_while_standing(char, choss)
    if won: 
        diag(char.name + " won the fight.")
    else: 
        diag(choss.name + " won the fight.")
    get_experience(char, 3)
    choss.upgrade(3)
    if won: 
        diag("Well done " + char.name + ". I knew my trust in you was well placed. Now about your father...")
    else: 
        diag("I didn't expect you to lose to him. Well, fate is a harsh teacher. Better luck next time!")
    
