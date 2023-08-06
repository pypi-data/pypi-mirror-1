#!/usr/bin/python

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

import sys
from random import seed, random
from time import time
from os import popen
from sets import Set
seed(time())

def min_nb_doms_p(name, nb):
    "true if at least nb domains are available"
    if nb == 0:
        return True
    nb_doms = 0
    for dom in (".info", ".org", ".net", ".com"):
        if len(popen("host -C "+name+dom+" 2>&1").read()) == 0:
            nb_doms += 1
            if nb_doms >= nb:
                return True
    return False

def dom_avails(name):
    # not completly good, we only check the SOA but that should do the
    # trick
    doms = []
    for dom in (".com", ".net", ".org", ".info"):
        if len(popen("host -C "+name+dom+" 2>&1").read()) == 0:
            doms.append(dom)
    return doms

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

if __name__ == "__main__":
    if len(sys.argv) != 6:
        print "USAGE: %s PROBS MIN_L MAX_L NB_W NB_D" % sys.argv[0]
        print "  PROBS is the language transition table"
        print "  MIN_L is the minimum desired word length"
        print "  MAX_L is the maximum desired word length"
        print "  NB_W  is the number of words to generate"
        print "  NB_D  is the number of free domain required (0 to 4)"
        sys.exit(1)
    tr3_prob = eval(open(sys.argv[1]).read())
    min_l = int(sys.argv[2])
    max_l = int(sys.argv[3])
    nb_w  = int(sys.argv[4])
    nb_d  = int(sys.argv[5])
    
    names = []
    tried = Set()
    while len(names) < nb_w:
        name = gen3_name(tr3_prob)
        if min_l <= len(name) <= max_l \
               and name not in tried \
               and name3_prob(tr3_prob, name) > 0.000000025 \
               and min_nb_doms_p(name, nb_d):
            print "%.010f: %s" % (name3_prob(tr3_prob, name), name)
            names.append(name)
        tried.add(name)

    # TODO: fix the scoring 
    #for prob, name in sorted([(name3_prob(tr3_prob, name), name)
    #                          for name in names]):
    #    print "%.010f: %s" % (name3_prob(tr3_prob, name), name)
    print "tried", len(tried), "names"
    print ", ".join(sorted(names))
    
