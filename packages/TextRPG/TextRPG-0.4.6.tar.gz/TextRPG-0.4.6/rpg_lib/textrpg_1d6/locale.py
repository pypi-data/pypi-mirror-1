#!/bin/env python
# encoding: utf-8 

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


'''Return localizable strings. 
'''


#### IMPORTS ####

# Obtain Charakters from yaml-files
from amov import Lokalisierung, Versionsverwaltung
# replaced the alias with the real directory. 

#### IMPORTS ####


#### CLASSES ####

class Locale(Lokalisierung.Lokalisierung):
    """Localized Strings.
    
    *args and **kwds makes sure, that we aren't confused, when we get more arguments than we expected."""
    def __init__(self,source="tag:1w6.org,2008:en_EN", *args,  **kwds):
        '''Basic creation of a single Char.'''
        # First call super, so that miltiple inheritance with char as first class can work. 
        super(Locale, self).__init__(tag=source, *args,  **kwds)
    
    def basic_data_yaml(self):
        """Return basic localizable Strings"""
        return """Name: en_EN

Input: 
  Please identify yourself: "Please type an email address or domain name as identifier for you as player: "
  Please give a name: "Please type a name for your char: "

Story:
  Greeter_1: Greetings,
  Greeter_2: You will have to prevail in this battle.
  Greeter_3: The first strike shall be yours.
  Greeter_4: Please select with the arrow keys or the number pad where you want to
    attack. Confirm with Enter or Return.
  Cease fighting: You had to cease fighting.
  You: You 
  comma: ", "
  Scored a hit: ", scored a hit."
  Your enemy: "Your enemy "
  took: " took "
  a deep wound: " a deep wound." 
  a critical wound: " a critical wound."
  You should stop: "You should stop this battle!"
  You take: ", take "
  Points of damage: " points of damage."
  Your turn to defend: Now it's your turn to defend yourself. Decide where you want to defend and counterattack.
  Your turn to attack: Now it's your turn to attack. Decide where you want to attack.

Battle Details: 
  Greeter_1: Details about the Battle
  First position set 1: First position set as 
  First position set 2: " - Counter position still needs to be set."
  Pos mod info 1: "Own position change mod: "
  Pos mod info sep 1: " [ "
  Pos mod info sep 2: " , "
  Pos mod info sep 3: " ] "
  Pos mod info 2: ", the others pos change mod: "
  Own position info 1: "self position_1: "
  Other position info 1: ", other position_1: "
  Attack prediction info: ", attack prediction modifier for defender: "
  Name-Role sep: ", "
  Attack-Choice sep: "-"
  Attack result info: " - attack result: "
  Weapon damage info: ", damage: "
  Armor value info: ", armor: "
  Fights against: fights against
  
Banner: 
  Game Over: Game Over
  Lose: You lost. 
  Win: You won. 
    
"""


#### CLASSES ####

#### Self-Test ####

def _test():
    import doctest
    doctest.testmod()

if __name__ == "__main__": 
    _test()
    locale = Locale()
    print locale.locale
    
#### Self-Test ####
