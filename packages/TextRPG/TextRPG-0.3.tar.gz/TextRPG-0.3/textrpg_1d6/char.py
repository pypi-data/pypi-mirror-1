#!/bin/env python
# encoding: utf-8 

# rpg-1d6 - A general roleplaying backend. 
#   http://rpg-1d6.sf.net
# Copyright © 2007 - 2007 Achim Zien

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston,
# MA 02110-1301 USA


'''
Characters and methods for use in schlachtfeld module.

Characters act on their own now and can be imported and saved via amov module.

Plans: 
    - Every skill has two assiciated attributes, which increase its value. 

Ideas: 
    - Save everything which happens to each soldier in an attribute of the soldier, so we can track his way through the battle. 
    
        This could be in the style: 
            - Jemor won a battle against Gwarach, but got severly wounded. 
            - Jemor lost the battle against Haske and left the battlefield. 
            - Jemor stayed in the medics tent. 
            - Jemor stayed in the medics tent. 
            - Jemor started into battle again. One of his wounds didn't bother him anymore. 
            - Jemor lost the Battle against Grishkar the beheader and left the battlefield for good. 

Doctests: 
    >>> katt = Char()
    >>> katt.sprache
    'Esperanto'
    >>> katt.value_and_striche_fertigkeiten(striche=11)
    (15, 11)
    >>> katt.value_and_striche_fertigkeiten(striche=4*3)
    (16, 12)
    >>> katt.value_and_striche_fertigkeiten(striche=13)
    (16, 13)
    >>> katt.value_and_striche_fertigkeiten(striche=14)
    (16, 14)
    >>> katt.value_and_striche_fertigkeiten(striche=15)
    (17, 15)
    >>> katt.value_and_striche_fertigkeiten(val=15)
    (15, 9)
    >>> katt.value_and_striche_fertigkeiten(val=18)
    (18, 18)
    >>> katt.amov.eigenschaften
    ' '
    >>> katt.amov.eigenschaften = {"Eleganz": {"Zahlenwert": 12}}
    >>> katt.amov.eigenschaften
    {'Eleganz': {'Zahlenwert': 12}}
    >>> katt.amov.fertigkeiten
    {'Nahkampf': {'Grundwert': 12, 'Striche': 3, 'Zahlenwert': 12}}

'''


#### IMPORTS ####

# for the fighting
from random import randrange as rnd
from random import shuffle
from random import random as rnd01
from random import choice
import math

# For storing values of dicts in other dicts
from copy import deepcopy

# For selection of armies through command line arguments: 
import sys

# EWS standard dice
import pmw6

# Name-Generator
import namen

# Obtain Charakters from yaml-files
from amov import Charakter, Versionsverwaltung
from amov.Object import _
# replaced the alias with the real directory. 

#### IMPORTS ####




#### Top-Level Objects ####

verbose = False #: Print output for debugging?

name_objekt = namen.Name()

# scatter for random attack values
atscatter = [3,2,1]

#### Top-Level Objects ####




#### WRAPPERS ####

def ews():
    """Do one roll with the plusminus d6 die (wrapper for a function in pmw6)."""
    return pmw6.pmw6()

def check(skill,MW):
    """Check if a given skill test reached a min-value (wrapper for a function in pmw6)."""
    return pmw6.check(skill,MW)

def ocheck(skill,MW):
    """Return the degree of success / failure for a skill check (wrapper for a function in pmw6)."""
    return pmw6.open_check(skill,MW)

def ocheck_and_res(skill,  MW):
    """Return the degree of success / failure for a skill check plus the reached value (wrapper for a function in pmw6)."""
    return pmw6.open_check_with_result(skill,MW)


def name_it(language=_("Esperanto")):
    '''Return a name corresponding to the characters language.'''
    return name_objekt.erzeuge(art=language) # ToDo: Fluszh the list of pregenerated names, when the language type changes. 
    
#### WRAPPERS ####




#### CLASSES ####

class Char(object):
    """A single soldier. Will be imported from either a prefab character file from amov or via a template
    
    *args and **kwds makes sure, that we aren't confused, when we get more arguments than we expected."""
    
    def __init__(self,source="tag:1w6.org,2008:Human",template=True,  *args,  **kwds):
        '''Basic creation of a single Char.'''
        # First call super, so that miltiple inheritance with char as first class can work. 
        super(Char, self).__init__(*args,  **kwds)
        
        # creation from amov template/char
        self.source = source
        self.ID = Versionsverwaltung.Versionen(self.source, _(u"Vorlagen")).neuste
        self.amov = Charakter.Charakter(self.ID)
        
        # rank
        self.name_me(template)
        self.description = self.amov.beschreibung
        self.sprache = self.amov.sprache
        
        # amov combat values
        # When we create him/her, the char is active
        self.active = True
        # and alive
        self.alive = True
        #: The damage a character can take before going down. 
        self.bTP = self.amov.kampfwerte[_('Trefferpunkte')]
        #: The wound value determines, how much damage suffices to inflict a wound on the character.  It's a List containing the value for deep wounds and for critical wounds. A deep wounds weakens the character (3 points off any skill and attribute), a critical wounds disables (the character has to roll, if he keeps standing). 
        self.WS = [self.amov.kampfwerte[_('Wundschwelle')],self.amov.kampfwerte[_('Wundschwelle')] * 3]
        #: The damage which te characters main weapon inflicts. 
        self.dam = self.amov.kampfwerte[_('Hauptwaffe')][_('Waffe')][_('Schaden')]
        #: The attack value of the character. 
        self.attack = self.amov.kampfwerte[_('Hauptwaffe')][_('Kampffertigkeit')][_('Zahlenwert')]
        #self.skill = self.amov.kampfwerte[_('Hauptwaffe')][_('Kampffertigkeit')][_('Name')]
        #: The armor value of the character. 
        self.arm = self.amov.schutz
        
        # variable schlachtfeld values
        self.TP = self.amov.kampfwerte.setdefault(_('Aktuelle Trefferpunkte'), self.bTP) #: The current Health Points of the Char. 
        #: An int, how often the char already managed to walk on, thought the TP were below 0. 
        self.number_of_ko_checks = 0
        self.active = True #: Shows if the the Char is active? 
        # Make sure that we have a wounds dict
        self.amov.kampfwerte.setdefault(_("Wunden"), {})
        # Get the physical wounds, if None are set, they are 0 each. 
        self.wounds = [self.amov.kampfwerte[_("Wunden")].setdefault(_(u'körperlich tief'), 0), self.amov.kampfwerte[_("Wunden")].setdefault(_(u'körperlich kritisch'), 0)] #: deep wounds, critical wounds
        # print self.wounds
        
        # Get the experience, either from the char, if it has it, or calculate it from all other values.
        self.amov.ladeGrunddaten().setdefault(_("Striche"), self.calculate_might()) #: The experience of the char. 
        
        #: The main weapon of the char
        self.weapon = self.amov.kampfwerte[_("Hauptwaffe")][_("Waffe")]
        
        #: The fighting skill of the char
        self.fight_skill = self.amov.kampfwerte[_("Hauptwaffe")][_("Kampffertigkeit")]
        
        #: The current armor of the char
        self.armor = self.amov.kampfwerte[_(u"Hauptrüstung")]
        
        
        # Get the morale
        
        if self.amov.eigenschaften == " " or self.amov.eigenschaften.setdefault(_("Morale"), {_("Zahlenwert"): 12})[_("Zahlenwert")] == 12: 
          self.morale = [12]
        else: 
          self.morale_dict = self.amov.eigenschaften.setdefault(_("Morale"), {})
          self.morale = [self.morale_dict.setdefault(_("Zahlenwert"), 12)]
    
    def get_attributes(self): 
        """Get the attributes for the attribute property, so it stays up to date."""
        attributes = self.amov.eigenschaften
        # Having no attributes should be an empty dict. This is necessary for correctly converting legacy characters. 
        if attributes == " ": 
            attributes = {}
            self.amov.eigenschaften = attributes
        return attributes
    
    def get_skills(self): 
        """Get the skills for the skill property, so it stays up to date."""
        skills = self.amov.fertigkeiten
        # recalculate the effective value from the base value and related attributes. 
        for i in skills: 
            bonus = 0 #: bonus from related attributes. 
            if _("Passende Eigenschaften") in skills[i]: 
                for j in skills[i][_("Passende Eigenschaften")]: 
                    bonus += pmw6.value_to_plusses(j[_("Zahlenwert")])
                skills[i][_("Zahlenwert")] = skills[i][_("Grundwert")] + bonus
        return skills
            
    def get_equipment(self): 
        """Get the skills for the skill property, so it stays up to date."""
        return self.amov.ausruestung
    
    # A property always gets loaded directly from the values, so it stays up to date. 
    # This avoids String to dict problems. 
    #: The attributes of the char. 
    attributes = property(fget=get_attributes)
    #: The attributes of the char. 
    skills = property(fget=get_skills)
    #: The equipment of the char. 
    equipment = property(fget=get_equipment)
    
    
    def save_data_into_char_dict(self): 
        """Save the data from the attributes back into the amov data. 
        
        This means copying all string attributes back into the attributes of the amov object. """
        # First transfer the ID which identifies the char back into the amov data
        self.amov.ID = self.ID
        # Then the chars language. 
        self.amov.sprache = self.sprache
        # Then its name
        self.amov.name = self.name
        # then its description
        self.amov.beschreibung = self.description
        
        # Now on to the battle values
        # Then its basic TP
        self.amov.kampfwerte[_('Trefferpunkte')] = self.bTP
        # And its wound treshold
        self.amov.kampfwerte[_('Wundschwelle')] = self.WS[0]
        # After that the damage of its weapon
        self.amov.kampfwerte[_('Hauptwaffe')][_('Waffe')][_('Schaden')] = self.dam
        # And the attack skill 
        self.amov.kampfwerte[_('Hauptwaffe')][_('Kampffertigkeit')][_('Zahlenwert')] = self.attack
        # Also the armor
        self.amov.schutz = self.arm
        # And the current TP
        self.amov.kampfwerte[_('Aktuelle Trefferpunkte')] = self.TP
        # Also the wounds, deep and critical
        self.amov.kampfwerte[_('Wunden')][_(u"körperlich tief")] = int(self.wounds[0])
        self.amov.kampfwerte[_('Wunden')][_(u"körperlich kritisch")] = int(self.wounds[1])
        # Save experience
        self.amov.ladeGrunddaten()[_("Striche")] = self.exp
        
    
    def save(self): 
        """Save the char into a file, incrementing the minor version, if there is already an existing one."""
        # First prepare the amov data
        self.save_data_into_char_dict()
        # Now call the character object to save itself
        self.amov.save(name=self.name)

    def __str__(self):
        ''' Hopefully nice printout for a soldier.'''
        if self.name is not None: 
            scribble = _('Name: ') + self.name
        else: 
            scribble = _("Unbekannter Charakter")
        scribble += '\n' + _('Sprache: ') + self.sprache
        return scribble
    
    def __lt__(self,  other):
        """Return, if the char is weaker than another char.
        
        We need to do this, because we don't want two chars to be treated as equal, just because they have the same exp (for example they would be seen as duplicates). """
        return (self.exp < other.exp)
    
    def __gt__(self,  other):
        """Return, if the char is stronger than another char.
        
        We need to do this, because we don't want two chars to be treated as equal, just because they have the same exp (for example they would be seen as duplicates). """
        return (self.exp > other.exp)
        

    def name_me(self, template):
        '''Give the Char a random name or import it from the file.'''
        if template:
            self.nametype = self.amov.sprache
            self.name = name_it(language=self.nametype)
        else:
            self.name = self.amov.name
        return


    def damage(self, tp=None, ws=None, hws=None):
        '''Damage a character and check for suvivial. Arguments: hitpoints, wounds, heavy wounds.'''
        # If we're given tp, we work directly with them. 
        if tp is not None and ws is None and hws is None: 
            # First substract the damage from the TP
            self.TP -= tp
            # Then check, if the tp suffice to cause a wound, but not a critical wound
            if self.WS[0] <= tp < self.WS[1]: 
                # And if it does, increase the number of wounds by one. 
                self.wounds[0] += 1
                # At last we check, if the char's still alive. 
                self.checkalive()
                # return a tuple with the new wound and jump out: (deep, critical)
                return 1, 0
            # If it suffices to do a critical wound, ouch! 
            elif self.WS[1] <= tp: 
                # You're out! (at least almost...)
                # Add a critical wound. 
                self.wounds[1] += 1
                # At last we check, if the char's still alive. 
                self.checkalive()
                # return a tuple with the new wound and jump out: (deep, critical)
                return 0, 1
            # If we get to this place, no wound was taken
            return 0, 0
            
        # If we get passed at least a wound, we first reduce the TP
        self.TP -= tp + (ws * self.WS[0]) + (hws * self.WS[1]) # self.WS is a list containing the wound value and the heavy wound value of the character. 
        
        # And then apply the taken wounds
        self.wounds[0] += ws
        self.wounds[1] += hws
        # At last we check, if the char's still alive. 
        self.checkalive()
        return


    def checkalive(self, base_att=None):
        '''Check if a character is still alive after being damaged.
        
        If no base_att is given, this uses the morale. 
        
        To see if a char is still active, we first look, if its TP are <= 0. 
        If they are we do one check against 12, to see if its still active. 
        
        After that we only do one check each time the TP fall to one (further) critical wound value below zero. 
        
        If the TP fall below (or to) 4 critical wound values below 0, the char is definitely dead. 
        
        TODO: Automatically use the correct base_att, for example constitution, or some alias inside the battle_values of the char. 
        
        '''
        
        # If no base att is given, we use the morale. 
        if base_att is None: 
            value = sum(self.morale)
        # else we use the given base_att
        else: 
            value = base_att
        
        # check, if the char is still able to fight. 
        # morale effects: for each morale over 15 > negative TP; for every 6 morale over 12 > max hwounds+1; for every 5 morale over 15 > max wounds+1
        if self.TP <= -self.number_of_ko_checks * self.WS[1]: 
            # First increase the number of ko checks, since this is one :) 
            self.number_of_ko_checks += 1
            # Do a check _without_ wound modifiers, that means a basic ews check. 
            # If the treshold of 4 checks is reached (that means, this is the 5th check), the char definitely goes down. 
            if self.number_of_ko_checks >= 5 or self.TP < -4*self.WS[1] or self.wounds[0] + 3*self.wounds[1] > 18: 
                # If he exceeded 5 KO checks, or his TP fall below 4 times the base attribute, or he got more than 18 wounds (same as TP too low), he's out and will die (see the call to die() below). 
                self.active = False
            else:
                # else it checks, if it can still stand. 
		# The first two KO checks are against 12, the others get consecutively harder.
		if self.number_of_ko_checks == 0:
	                self.active = check(value, MW=12)
		else: 
                	self.active = check(value, MW=(12 + 3*(self.number_of_ko_checks -1)))
			# these are deadly if missed.
			if not self.active:
				self.die()
        
        # In any case, if the TP fall below 4 times the base attribute, or he got more than 18 wounds, he dies. 
        if self.TP < -4*self.WS[1] or (self.wounds[0] + 3*self.wounds[1]) > 18: 
             self.active = False
             self.die()
        return
    
    
    def die(self):
        """Let the Character die."""
        # Don't fight anymore
        self.active = False
        # And don't breathe anymore :) 
        self.alive = False
        
    def check(self, value, mods=[], MW=9):
        '''Make a check with mods on any skill, atttribute or similar. Return if the check was made (True or False). 
        
        Wounds reduce the result. 
        '''
        # mods is a list modifiers which affect the attack roll. 
        return check(value + sum(mods) - 3*(self.wounds[0]+2*self.wounds[1]), MW=MW)
        
    def roll(self, value, mods=[]):
        '''Make a check with mods on any skill, atttribute or similar. Return the absolute result of the roll. 
        
        Wounds reduce the result. 
        '''
        # mods is a list modifiers which affect the attack roll. 
        return value + sum(mods) + ews() - 3*(self.wounds[0]+2*self.wounds[1])

    
    def check_skill(self, skill_name, MW=9, related_skills=[], related_attributes=[], mods=[]):
        """Do a skill check against a target number.
        
        Wounds are taken into account as modifiers automatically. 
        """
        # If the char has skills and the skill exists, do a check on it. 
        return self.check(self.get_effective_skill_value(skill_name, related_skills=[], related_attributes=[]), mods=mods, MW=MW)


    def get_effective_skill_value(self, skill_name, related_skills=[], related_attributes=[]): 
        """Get the effective value for tests. 
        
        This doesn't take wounds into account, as they are already taken account in the method self.check()."""
        if skill_name in self.skills.keys(): 
            return self.skills[skill_name][_("Zahlenwert")]
        # If the skill doesn't exist in Fertigkeiten, see if we can do the check on some related skill, but with a malus of 3. 
        # TODO: Implement Jobs and background. 
        else: 
            for i in related_skills: 
                if i in self.skills.keys(): 
                    return self.skills[i][_("Zahlenwert")] - 3
        # If the char has no skills, see if we can check against a related attribute, but with a malus of 9. 
        for i in related_attributes: 
            if i in self.attributes.keys() and self.attributes[i][_("Zahlenwert")] >= 12: 
                return self.attributes[i][_("Zahlenwert")] - 9
        # If the char has no fitting attributes or skills, just use the default attribute of 12. 
        return 12 - 9
        
    
    
    def do_attack(self,  mods=[]):
        '''
        Make an attack-roll to be compared to the enemy's roll. Base method to evaluate comabat.
        Contributions: base skill, weapon, armor, +-d6, wounds (deep: each -3, crit: each -6 while in combat), , group situation (strategy & bias), morale bonus /each point over 12)
        '''
        #print self.name, self.host
        # mods is a list modifiers which affect the attack roll. 
        return self.roll(self.attack, mods=mods) + self.dam + self.arm 
        
    def attack_roll(self,  mods=[]):
        '''
        Make an attack-roll to be compared to the enemy's roll. Base method to evaluate comabat.
        Contributions: base skill, weapon, armor, +-d6, wounds (deep: each -3, crit: each -6 while in combat), , group situation (strategy & bias), morale bonus /each point over 12)
        '''
        #print self.name, self.host
        # mods is a list modifiers which affect the attack roll. 
        return self.roll(self.attack, mods=mods)


    def calculate_might(self,  second_run=False):
        # determine the power of the opposing character
        might = 0
        # Add all Striche of the Eigenschaften to the might
        if self.amov.eigenschaften != " ": 
            for i in self.amov.eigenschaften.keys(): 
                might += self.amov.eigenschaften[i].setdefault("Striche",  self.get_necessary_striche_for_obj({i: self.amov.eigenschaften[i]}))
        # Now add all Striche of the Fertigkeiten to the might
        if self.amov.fertigkeiten != " ": 
            for i in self.amov.fertigkeiten.keys(): 
                might += self.amov.fertigkeiten[i].setdefault("Striche",  self.get_necessary_striche_for_obj({i: self.amov.fertigkeiten[i]}))
        if might == 0: 
            if second_run: 
                print self.amov.eigenschaften,  self.amov.fertigkeiten
                raise ValueError("Char has no experience and can't do anything!")
            self.upgrade(0)
            return self.calculate_might(second_run=True)
        else: 
            return might
    
    def set_experience(exp): 
        """Set the experience of the char. Exp can't be decreased this way. 
        
        This is a thin wrapper around upgrade()
        
        It is used to be able to handle exp as property, so people can just say: 
        char.exp = 10
        
        instead of 
        
        char.upgrade(10-char.exp)
        
        @param exp: The new experience value.
        @type exp: float or int.
        """
        if exp > self.exp: 
            self.upgrade(exp - self.exp)
            return self.exp
        else: 
            return False
    
    # The experience of the char as property, so it is always up to date. 
    exp = property(fget=calculate_might, fset=set_experience)
    
    
    def upgrade(self,expadd,object=('weighted',[])):
        '''
        Randomly enhance the characters skills and attributes. 
        
        Dashes are spent and collected until a higher level is reached. Higher attributes and skills are preferred, thus specializing the character.
        expadd: number of dashes (float - subdashes included)
        object: object of enhancement; 'attribute', 'skill', 'random' or 'weighted' + name of object; standard is 'random'
        
        How to call: 
            >>> char = Char()
            # Upgrade a random value
            >>> char.upgrade(3, object=('random', 0))
            # Upgrade a specific skill (cooking)
            >>> char.upgrade(3, object=("skill", "cooking"))'
            # Upgrade a specific attribute
            >>> char.upgrade(3, object=("attribute", "sensitivity"))
            # Upgrade weighted with a list of things to upgrade.
            >>> char.upgrade(3, object=("weighted", [("attribute",  "sensitivity", 1), ("skill", "cooking", 2)]) # [(cathegory, name, weight), (...)]
        
        Plans: Call the function with a list of Abilities and Attributes, which get improved in the situation in which the Char got the dashes. 
        '''
        # select proper attribute / skill
        if object[0] == 'random':
            listing = []
            # If the char already has Eigenschaften, use a listing of Eigeschaften and Fertigkaietn as base for improvement. 
            if self.amov.eigenschaften != " " and self.amov.fertigkeiten != " ": 
                #Add all Eigenschaften and Fertigkeiten to the listing. 
                for i in self.amov.fertigkeiten.keys(): 
                    listing.append({i: self.amov.fertigkeiten[i]})
                # Now add all Fertigkeiten to the listing. 
                for i in self.amov.eigenschaften.keys(): 
                    listing.append({i: self.amov.eigenschaften[i]})
            elif self.amov.fertigkeiten != " ": # Just use the list of existing Fertigkeiten. 
                for i in self.amov.fertigkeiten.keys(): 
                    listing.append({i: self.amov.fertigkeiten[i]})
            elif self.amov.eigenschaften != " ": # Just use the list of existing Eigenschaften. 
                for i in self.amov.eigenschaften.keys(): 
                    listing.append({i: self.amov.eigenschaften[i]})
            else: 
                raise ValueError("Char has no Eigenschaften an no Fertigkeiten!")
                
            if len(listing) > 1: 
                obj = choice(listing)
            else: obj = listing[0]
            
        elif object[0] in [_('attribute'), _('skill')]:
            if object[0] == _('skill') and self.amov.fertigkeiten != " ":
                listing = self.amov.fertigkeiten
            elif object[0] == _('attribute') and self.amov.eigenschaften != " ":
                listing = self.amov.eigenschaften
            else: listing = None
            # If the object is part of the Fertigkeiten or Eigenschaften, 
            # Set obj as the subtree of the listing dictrionary. 
            if listing is not None and object[1] in listing.keys():
                obj = {object: listing[object[1]]}
            else:
                # add a new skill or attribute
                # For this we add a new key to the respective list (eigenschaften or fertigkeiten)
                # And map that key an an empty dictionary. The base values will be added later on. 
                if object[0] == _("skill"): 
                    # First make sure that the skills are a dict. 
                    if self.amov.fertigkeiten == " ": 
                        self.amov.fertigkeiten = {}
                    # Then add object 1. 
                    self.amov.fertigkeiten.setdefault(object[1], {})
                    obj = {object: self.amov.fertigkeiten[object[1]] }
                elif object[0] == _("attribute"): 
                    # First make sure attributes are a dict. 
                    if self.amov.eigenschaften == " ": 
                        self.amov.eigenschaften = {}
                    # then add object 1. 
                    self.amov.eigenschaften.setdefault(object[1], {})
                    obj = {object: self.amov.eigenschaften[object[1]] }
                if verbose: # Provide some feedback: What kind of value was added, and which one. 
                    print 'Added',  object[0],  object[1]

                
        elif object[0] == 'weighted':
            #: The weightlist contains tuples with the name and the weight of each to-be-increased value.
            weightlist = []
            #: The valuelist contains the possible objects, without weighting. object: {(cathegory, name): {}} - cathegory is 'skill' or 'attribute'
            valuelist = []
            # Add all avaible Eigenschaften and Fertigkeiten as sub-dictionaries to the valuelist. 
            if self.amov.eigenschaften != " " and self.amov.fertigkeiten != " ": 
                for i in self.amov.fertigkeiten.keys(): 
                    valuelist.append({(_("skill"), i ): self.amov.fertigkeiten[i]})
                for i in self.amov.eigenschaften.keys(): 
                    valuelist.append({(_("attribute"), i ): self.amov.eigenschaften[i]})
            elif self.amov.fertigkeiten != " ": # Just use the existing Fertigkeiten. 
                for i in self.amov.fertigkeiten.keys(): 
                    valuelist.append({(_("skill"), i ): self.amov.fertigkeiten[i]})
            elif self.amov.eigenschaften != " ": # Just use the existing Eigenschaften. 
                for i in self.amov.eigenschaften.keys(): 
                    valuelist.append({(_("skill"), i): self.amov.eigenschaften[i]})
            else: 
                raise ValueError("Char has no Eigenschaften and no Fertigkeiten!")
            # Get the biasing for each value by determining how many striche have already been spent without increasing it (+1). 
            # This gives a bias towards advancing higher values. 
            for i in valuelist: 
                for j in i.keys():
                    #: The lowest number of Strichen needed to reach this value. 
                    necessary_striche = self.get_necessary_striche_for_obj(i)
                    #: Biasing determines, how much weight this value gets. 
                    biasing = 1 + i[j].get(_('Striche'),  necessary_striche) - necessary_striche
                    if biasing < 1: 
                        print "Biasing < 1 ! ",  i,  "necessary_striche:",  necessary_striche
                        raise ValueError("Biasing < 1 ! " + str(i) + " necessary_striche: " + str(necessary_striche))
                    weightlist.append((j,  biasing))
            
            # Also add the given list of values to improve. 
            for i in object[1]: 
                weightlist.append(((i[0], i[1]), i[2]))
            
            problist = [] #: A list containing as many instances of each value as it's weight states. 
            for i in range(len(weightlist)):
                for j in range(int(weightlist[i][1])):
                    # Append the name of the item as often as its weight states
                    problist.append(weightlist[i][0]) # The name of the item
            # Determine the weight of all objects added together
            weights_added_together = len(problist)
            dice = rnd01() * weights_added_together
            # in some corner cases a float can be converted to an int with the upper boundary of the float, 
            # In this case weights_added_together. We have to avoid that cornercase. 
            # Example of that cornercase: int(0.99999999999999999) == 1
            while int(dice) == weights_added_together: # If those were equal, it would select the item at position len(problist), which is out of range. 
                dice = rnd01() * weights_added_together
            selected = problist[int(dice)]
            #: The object contains the ability to be raised, only its content, not its name. 
            for i in valuelist: 
                if i.has_key(selected): 
                    obj = i
            # Check if object is defined. 
            try: 
                a = obj
            # If not, it is a new value. 
            except: 
                    # Selected value is not in  the valuelist, so it's a skill or attribute the char doesn't yet have. 
                    # If it's a skill, add it to the skills
                    if selected[0] == _("skill"): 
                        # If we don't yet have skills, make skills a dict. 
                        if self.amov.fertigkeiten == " ": 
                            self.amov.fertigkeiten = {}
                        # Now add the skill
                        self.amov.fertigkeiten[selected[1]] = {}
                        # And set it as the object to raise
                        obj = {selected: self.amov.fertigkeiten[selected[1]]}
                    # If it's an attribute, add it. 
                    if selected[0] == _("attribute"): 
                        # If we don't yet have attributes, make attributes a dict. 
                        if self.amov.eigenschaften == " ": 
                            self.amov.eigenschaften = {}
                        # Now add the attribute
                        self.amov.eigenschaften[selected[1]] = {}
                        # And set it as the object to raise. 
                        obj = {selected: self.amov.eigenschaften[selected[1]]}
                    
        # Now we know which ability or attribute we want to raise. Say so: 
        if verbose: 
            print self.name, "raised",  obj.keys()[0],  "with",  expadd,  "Strichen", 
        # And save it for later use.
        obj_before = deepcopy(obj)
        
        # As next step, we need to determine, if it gets raised, and by how much. 
        
        # First get the value of the selected object. 
        # If it's a Fertigkeit, get the Grundwert. 
        if self.amov.fertigkeiten != " ": 
            for i in self.amov.fertigkeiten.keys(): 
                # Check if it has a skill key i
                if obj.has_key((_("skill"), i)): 
                    sub_obj = obj[(_("skill"), i)]
                    val = sub_obj.setdefault(_("Grundwert"),  sub_obj.setdefault(_("Zahlenwert"),  3))
                    # all skills / attributes should have a 'Striche' item
                    striche_old = sub_obj.setdefault(_("Striche"),  self.value_and_striche_fertigkeiten(val=sub_obj.setdefault(_("Grundwert"),  3))[1])
                    sub_obj.setdefault(_("Striche"),  striche_old)
                    # add xp, if applicable raise skill / attribute
                    sub_obj[_('Striche')] += expadd
                    sub_obj[_("Grundwert")] = self.value_and_striche_fertigkeiten(striche=sub_obj[_('Striche')] )[0]
                    if sub_obj[_("Zahlenwert")] < sub_obj[_("Grundwert")] : 
                        sub_obj[_("Zahlenwert")] = sub_obj[_("Grundwert")] #TODO: We need a character method, which gets the Zahlenwert from the Grundwert. 
    
        # If it's an attribute, get the Zahlenwert. 
        if self.amov.eigenschaften != " ": 
            for i in self.amov.eigenschaften.keys(): 
                if obj.has_key((_("attribute"), i)): 
                    sub_obj = obj[(_("attribute"), i)]
                    striche_old = sub_obj.setdefault(_("Striche"),  self.value_and_striche_eigenschaften(val=sub_obj.setdefault(_("Zahlenwert"),  12))[1])
                    sub_obj[_("Striche")] = striche_old + expadd
                    sub_obj[_("Zahlenwert")] = self.value_and_striche_eigenschaften(striche=sub_obj[_("Striche")])[0]
        
        if verbose: 
            print "to",  obj # finishing upgrade line of output
        self.attack = self.amov.kampfwerte[_('Hauptwaffe')][_('Kampffertigkeit')][_('Zahlenwert')]
        return obj_before, obj
    
    
    def get_necessary_striche_for_obj(self,  obj):
        necessary_striche = 0
        if self.amov.fertigkeiten != " ": 
            for i in self.amov.fertigkeiten.keys(): 
                if obj.has_key(i): 
                    # Every Fertigkeit needs a Grundwert
                    obj = obj[i]
                    val = obj.setdefault(_("Grundwert"),  obj.setdefault(_("Zahlenwert"),  3))
                    # all skills / attributes should have a 'Striche' item
                    striche = obj.setdefault(_("Striche"),  self.value_and_striche_fertigkeiten(val=obj.setdefault(_("Grundwert"),  3))[1])
                    necessary_striche = self.value_and_striche_fertigkeiten(val=obj.setdefault(_("Grundwert"),  3))[1]
        if self.amov.eigenschaften != " ": 
            for i in self.amov.eigenschaften.keys(): 
                if obj.has_key(i): 
                    obj = obj[i]
                    striche = obj.setdefault(_("Striche"),  self.value_and_striche_eigenschaften(val=obj.setdefault(_("Zahlenwert"),  12))[1])
                    necessary_striche = self.value_and_striche_eigenschaften(val=obj.setdefault(_("Zahlenwert"),  12))[1]
        return necessary_striche
    
    
    def value_and_striche_fertigkeiten(self,  val=None,  striche=None):
        """Return value and striche"""
        return pmw6.value_and_striche_fertigkeiten(val=val, striche=striche)
    
    
    def value_and_striche_eigenschaften(self,  val=None,  striche=None):
        """Return value and striche."""
        return pmw6.value_and_striche_eigenschaften(val=val, striche=striche)
        
        
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
            # Now check for damage (we hit)
            # The damage consists of several factors. 
            # First the difference between the attack rolls. 
            self.damage_other += attack_self - attack_other
            # Then the damage of our weapon. 
            self.damage_other += self.dam
            # And substracted the armor of the other. 
            self.damage_other -= other.arm
        
        # Clean out negative damage. If the damage is below zero, the armor caught all damage. 
            if self.damage_other < 0: 
                self.damage_other = 0
            
            # Now actually do the damage. This returns a tuple: (new deep wounds, new critical wounds)
            deep_wounds_other, critical_wounds_other = other.damage(tp=self.damage_other)
        
        # If the other rolls better
        elif attack_self < attack_other: 
            won = False
            # Check for our damage (the other hit)

            # The damage consists of several factors. 
            # First the difference between the attack rolls. 
            self.damage_self += attack_other - attack_self
            # Then the damage of our weapon. 
            self.damage_self += other.dam
            # And substracted the armor of the other. 
            self.damage_self -= self.arm

            # Clean out negative damage. If the damage is below zero, the armor caught all damage. 
            if self.damage_self < 0: 
                self.damage_self = 0
            
            # Now actually take the damage. This returns a tuple: (new deep wounds, new critical wounds)
            deep_wounds_self, critical_wounds_self = self.damage(tp=self.damage_self)

        # If we get the same result, the attacker wins, us. 
        else: 	
            won = True
            # Now check for damage (we hit)
            # The damage consists of several factors. 
            # First the difference between the attack rolls. 
            self.damage_other += attack_self - attack_other
            # Then the damage of our weapon. 
            self.damage_other += self.dam
            # And substracted the armor of the other. 
            self.damage_other -= other.arm
            
            # Clean out negative damage. If the damage is below zero, the armor caught all damage. 
            if self.damage_other < 0: 
                self.damage_other = 0
            
            # Now actually do the damage. This returns a tuple: (new deep wounds, new critical wounds)
            deep_wounds_other, critical_wounds_other = other.damage(tp=self.damage_other)
        	
        return won, [deep_wounds_self, critical_wounds_self, self.damage_self], [deep_wounds_other, critical_wounds_other, self.damage_other]


    def fight_one_roll_battle(self, other):
        """Fight a battle with the one roll system (one roll decides)."""
        
        # attack rolls
        res = self.do_attack() - other.do_attack()
        
        # damage, formatting: (tp, wounds, heavy wounds)
        # style-formatting:  (skill mod, (win own damage[base,stepsize]), (loose own damage[base,stepsize]), special pars
        if res == 0:
            self.damage(0,3,0)
            other.damage(0,3,0)
            if verbose: 
                print "Both are still standing but wounded (or dead) - none won the battle."
            # We don't need to check anything else. 
            return 
        else:
            if res > 0:
                winnerc = self
                loserc = other
            else:
                winnerc = other
                loserc = self
            res = abs(res)
            
            # TODO: Add battle styles again (from BatteField)
            
            # First get the damage for both
            winner = max(3-res/3, 0)
            loser = max(3+res/3, 0)
            if verbose:
                print winnerc.name, "won against", loserc.name
            
            # Then let the winner take damage
            winnerc.damage(0,winner,0)
            if verbose: 
                print winnerc.name, "takes", winner, "wounds." 
            
            # And let the loser take damage    
            loserc.damage(0,loser,0)
            # The loser goes down
            loserc.active = False
            
            if verbose: 
                print loserc.name, "takes", loser, "wounds."
            

    def get_battle_result_values(self): 
        """Return the values which change in battle."""
        return {"TP": self.TP, "Wounds [deep, critical]": self.wounds, "Active": self.active, "Alive": self.alive}
        
    
    def fill_missing_values(self):
        """Fill in missing values in the charsheets. """
        pass # TODO: Move all sheet-cleaning and sheet-filling code into this method. 



#### CLASSES ####

#### Self-Test ####

def _test():
    import doctest
    doctest.testmod()

if __name__ == "__main__": 
    _test()
    katt = Char(template=False)
    katt.amov.eigenschaften = {"Eleganz": {"Zahlenwert": 12}}
    print "Before Upgrade"
    print katt.amov.fertigkeiten
    print katt.amov.eigenschaften
    print "Add  3 dashes"
    katt.upgrade(3)
    print "After Upgrade"
    print katt.amov.fertigkeiten
    print katt.amov.eigenschaften
    print "Saving char."
    katt.save()
#### Self-Test ####
