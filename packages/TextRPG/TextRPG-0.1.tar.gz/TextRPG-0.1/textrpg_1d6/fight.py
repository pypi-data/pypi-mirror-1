#!/usr/bin/env python
# encoding: utf-8

###########################################################################
#    Copyright (C) 2007 by Achim Zien und Arne Babenhauserheide                                      
#    <arne_bab@web.de>                                                             
#
# Copyright: See COPYING file that comes with this distribution
#
###########################################################################

"""Calculate a fight between two chars (given as list) according to the EWS One Roll Fight system."""

verbose = False

#### imports ####

#### /imports ####

#### Fonctions ####

def fight(chars):
    """Calculate a fight between two individuals with the One Roll fight system
    
    Plans: 
        - Add Fatigue, since each single fight drains each fighter, so people can't fight forever with their full strength, Fatigue is an attribute. From this we determine a fatigue value (2*Fatigue). If this falls to 1/2, the fighter gets 1 point malus. If it falls to 1/6th, the fighter gets 3 points malus. If it falls to 0, the fighter gets 6 points malus ans has to check, if he stays standing. The he has to check if he stays standing again each time, the fatigue value drops below a multiple of the Fatigue attribute below zero. At fatigue value = -4x Fatigue attribute, the fighter falls unconscious. 
    """
    
    # If we have only two chars, we just let them battle it out
    if len(chars) == 2: 
        chars[0].fight_one_roll_battle(chars[1])
    else: 
        # TODO: Group battle isn't implemented yet
        raise Exception("Mass battle isn't implemented, yet")

    

#### /Functions ####

#### Self-Test ####

if __name__ == "__main__": 
    from schlachtfeld.amov import Charakter, Versionsverwaltung
    from schlachtfeld.Char import *
    verbose = true
    chars = [Char() for i in range(2)]
    #for i in range(2):
        #char = Char()
        #chars.append(char)
    print "Characters:\n", chars
    print "\nStarting the fight:"
    fight(chars)
    

#### /Self-Test ####
