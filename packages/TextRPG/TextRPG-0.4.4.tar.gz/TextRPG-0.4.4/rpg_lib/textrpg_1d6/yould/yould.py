#!/usr/bin/python
# encoding: utf-8

# Yould - A name generator generator
# This program was initially written by © Yannick Gingras - 2007

# Is was adapted by © Arne Babenhauserheide in 2007. 

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

#### Imports ####

from sys import exit as sys_exit
from sys import argv as sys_argv
from random import seed, random
seed() # Seed as the os states, or from time

#### Imports ####

#### Control Parameters #### 

maximum_useful_probability = 0.0025

min_probability = 0.0000000025
max_probability = 0.00025

#### Control Parameters #### 

def get_c(probs, draw):
    tot = 0
    for prob, c in probs:
        tot += prob
        if tot >= draw:
            return c
    return c

def gen3_name(tr3_prob):
    choices = []
    pprev = prev = None
    c = get_c(tr3_prob[(None, None)], random())
    while c != None:
        choices.append(c)
        pprev = prev
        prev = c
        c = get_c(tr3_prob[(pprev, prev)], random())
        
    return "".join(choices)

def name3_prob(tr3_prob, name):
    prob = 1.0
    pprev = prev = None
    for c in name:
        prob *= filter(lambda rec:rec[1] == c,
                       tr3_prob[(pprev, prev)])[0][0]
        pprev = prev
        prev = c
    return prob * filter(lambda rec:rec[1] == None,
                         tr3_prob[(pprev, prev)])[0][0]

def generate_names(tr3_prob, min_l, max_l, nb_w, nb_d, min_prob = min_probability, max_prob = max_probability): 
    
    names = []
    tried = []
    while len(names) < nb_w:
        name = gen3_name(tr3_prob)
        # catch bad set min_prob and max prob
        # Minuímum probaility 
        if min_prob > maximum_useful_probability / 28: 
            min_prob = maximum_useful_probability / 28
        # min_prob needs to be at least factor 28 smaller than max_prob. Experimental result
        if min_prob > max_prob / 28: 
            if max_prob < maximum_useful_probability: # min-prob was badly set
                min_prob = max_prob / 28
            else: # max-prob was badly set.
                max_prob = min_prob * 28
        if min_l <= len(name) <= max_l \
               and name not in tried \
               and name3_prob(tr3_prob, name) > min_prob \
               and name3_prob(tr3_prob, name) < max_prob:
            # print "%.010f: %s" % (name3_prob(tr3_prob, name), name)
            names.append(name)
        if name not in tried: 
            tried.append(name)

    # TODO: fix the scoring 
    #for prob, name in sorted([(name3_prob(tr3_prob, name), name)
    #                          for name in names]):
    #    print "%.010f: %s" % (name3_prob(tr3_prob, name), name)
    return names #, tried

def print_names(names, tried): 
    print "tried", len(tried), "names"
    print ", ".join(sorted(names))
    
#### Self-Test ####

if __name__ == "__main__":
    if len(sys_argv) != 6:
        print "USAGE: %s PROBS MIN_L MAX_L NB_W NB_D" % sys_argv[0]
        print "  PROBS is the language transition table"
        print "  MIN_L is the minimum desired word length"
        print "  MAX_L is the maximum desired word length"
        print "  NB_W  is the number of words to generate"
        print "  NB_D  is the number of free domain required (0 to 4)"
        sys_exit(1)
    tr3_prob = eval(open(sys_argv[1]).read())
    min_l = int(sys_argv[2])
    max_l = int(sys_argv[3])
    nb_w  = int(sys_argv[4])
    nb_d  = int(sys_argv[5])
    names = generate_names(tr3_prob, min_l, max_l, nb_w, nb_d)
    print_names(names, "")

#### Self-Test ####

