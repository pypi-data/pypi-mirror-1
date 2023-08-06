#!/bin/env python
# This Python file uses the following encoding=utf-8

# Schlachtfeld - Großkämpfe im EWS System
#   http://rpg-tools-1d6.sf.net
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

"""Do tests/checks (skills, etc.) according to the ±W6 rules => Throw a die."""


#### IMPORTS ####
from random import randint as rnd
#### IMPORTS ####


#### FUNCTIONS ####

def pmw6():
    """Throw the ±W6/±D6 die."""
    tmp = rnd(0,5)
    count = 1
    if tmp in [0,5]:
            while tmp == rnd(0,5):
                    count += 1
    wurf = count*ews[tmp]
    return wurf

def check(skill, MW):
    """Check if the throw reaches a target number (MW)."""
    if skill + pmw6() >= MW:
        return True
    else:
        return False
                
def open_check(skill, MW):
    """Check by how far we manage to beat the target number, or by how far we lose to it."""
    return skill - MW + pmw6()
    
def open_check_with_result(skill,  MW):
    """Check, by how far we beat (or get beaten by) a target number and also return, which absolute value we reach."""
    res = skill + pmw6()
    return res - MW,  res

# Convert between different represenations for skill values. 

def value_to_plusses(value=12, thing="attribute"): 
    """Return the value in effective plusses for attributes and skills. 
    @param thing: What is checked: attribute or skill. 
    @type thign: String. 
    """
    if thing == "attribute": 
        return round((value-12) / 3.0)
    elif thing == "skill": 
        if value <= 6: 
            return 0
        elif value == 9: 
            return 1
        else: 
            return round((value - 9) / 3.0)

# Convert between value and Strichen. 


    

def value_and_striche_fertigkeiten(val=None,  striche=None):
    """Return value and striche"""
    striche_fertigkeiten = [3,  6, 9, 12]
    # First we do the case, when we get striche and want a value
    # For a low number of striche, this is quite easy. 
    if striche is not None and striche <= 3: 
        val = striche_fertigkeiten[int(striche)]
        return val,  striche
    # for higher numbers of strichen, itthe necessary list is a bit longer. 
    elif striche is not None and striche > 3: 
        # first create an aggregator
        necessary_striche = 3
        striche_per_point = 2
        effective_value = 12
        # We raise the value until the necessary_striche is higher of equal to the striche. 
        # If it's higher, we reduce the value afterwards. 
        # add all values together, up to the number of strichen. 
        while necessary_striche < striche: 
            effective_value += 1
            necessary_striche += int(striche_per_point + 0.1) # this +0.1 is necessary to avoid some crazy rounding down at 2.0
            striche_per_point += 1/3.0
        if necessary_striche > striche: 
            effective_value -= 1
            necessary_striche -= int(striche_per_point)
        return effective_value,  striche
    
    # If we have a value, we return the number of necessary_striche, 
    # If teh value is lower than or equal to 12, it's easy to get the striche 
    # by inverse searching in the striche_fertigkeiten list. 
    if val is not None and val <= 12: 
        necessary_striche = striche_fertigkeiten.index(val)
        return val,  necessary_striche 
    # If the value is higehr than 12, we increase the effective_value in steps, 
    # until we reach the given value, increasing the striche as by the 1d6 vobsy rules. 
    elif val is not None and val > 12: 
        necessary_striche = 3
        striche_per_point = 2
        effective_value = 12
        while effective_value < val: 
            effective_value += 1
            necessary_striche += int(striche_per_point + 0.1) # this +0.1 is necessary to avoid some crazy rounding down at 2.0
            striche_per_point += 1/3.0
        return effective_value,  necessary_striche    


def value_and_striche_eigenschaften(val=None,  striche=None):
    """Return value and striche."""
    vorzeichen = 1
    if striche is not None and striche < 0: 
        striche = -striche
        vorzeichen = -1
    if striche is not None and striche >= 0: 
        # first create an aggregator
        necessary_striche = 0
        striche_per_point = 1
        effective_value = 12
        # We raise the value until the necessary_striche is higher of equal to the striche. 
        # If it's higher, we reduce the value afterwards. 
        # add all values together, up to the number of strichen. 
        while necessary_striche < striche: 
            effective_value += 1
            necessary_striche += int(striche_per_point + 0.1) # this +0.1 is necessary to avoid some crazy rounding down at 2.0
            striche_per_point += 1/3.0
        if necessary_striche > striche: 
            effective_value -= 1
            necessary_striche -= int(striche_per_point)
        if vorzeichen == 1: 
            return effective_value,  striche
        else: 
            return 24 - effective_value,  -striche
    
    if val is not None and val < 12: 
        val = 24 - val
        vorzeichen = -1
    # If the value is higher than 12, we increase the effective_value in steps, 
    # until we reach the given value, increasing the striche as by the 1d6 vobsy rules. 
    if val is not None and val >= 12: 
        necessary_striche = 0
        striche_per_point = 1
        effective_value = 12
        while effective_value < val: 
            effective_value += 1
            necessary_striche += int(striche_per_point + 0.1) # this +0.1 is necessary to avoid some crazy rounding down at 2.0
            striche_per_point += 1/3.0
        if vorzeichen == 1: 
            return effective_value,  necessary_striche
        else: 
            return 24 - effective_value,  -necessary_striche

#### FUNCTIONS ####


#### GAME PARS ####
ews = [-5, -3, -1, 2, 4, 6]
#### GAME PARS ####


#### SELF CHECK ####
if __name__ == '__main__':
        store = []
        for i in range(100000):
                store.append(pmw6())
        print 'min max'
        print min(store), max(store)
#### SELF CHECK ####
