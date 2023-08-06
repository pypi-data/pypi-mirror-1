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

# Adapted, so that it can also take non-gutenberg texts

import sys

from string import ascii_lowercase
from pprint import pprint

ONLY_READ_GUTENBERG_TEXTS = True

ltrs = tuple(ascii_lowercase)

BODY_TAG = " OF THE PROJECT GUTENBERG EBOOK"

MIN_W = 5
MAX_W = 14

def tokenize(line):
    "return the list of 'good' words on this line"
    words = []
    start = 0
    for i in range(len(line)-1):
        if line[i+1] not in ltrs:
            if line[start] in ltrs:
                word = line[start:i+1]
                if MIN_W <= len(word) <= MAX_W:
                    words.append(word)
                start = i+1
        elif line[start] not in ltrs:
            start = i+1
    return words
            

if __name__ == "__main__":
    tr3_freq = {} # ex: trs_freq[('l', 'a')] = (12, {'a':8, 'c':4})
    prev = pprev = None

    # train
    for f in sys.argv:
        in_body = False
        for line in open(f):
            # The following makes sure that we only read the Text from Gutenberg-ebooks, but makes this script ignore any non-gutenberg texts. 
            if ONLY_READ_GUTENBERG_TEXTS: 
                if not in_body:
                    if line.find("START"+BODY_TAG) == -1:
                        continue
                    else:
                        in_body = True
                if line.find("END"+BODY_TAG) != -1:
                    break

            for word in tokenize(line.lower()+"\n"):
                prev = pprev = None
                for c in word:
                    nb_trs, trs_h  = tr3_freq.get((pprev, prev), (0, {}))
                    trs_h[c] = trs_h.get(c, 0) + 1
                    tr3_freq[(pprev, prev)] = (nb_trs+1, trs_h)

                    pprev = prev
                    prev = c
                nb_trs, trs_h  = tr3_freq.get((pprev, prev), (0, {}))
                trs_h[None] = trs_h.get(None, 0) + 1
                tr3_freq[(pprev, prev)] = (nb_trs+1, trs_h)
                            
    # build prob tables
    # ex: trs_prob[('c', 'r')] = [(.1, 'e'), (.07, 'a'),...,(.001, 'z')]
    tr3_prob = {}
    for k in tr3_freq.keys():
        nb_trs, trs_h = tr3_freq[k]
        tr3_prob[k] = [ (1.0*freq/nb_trs, nc)
                        for nc, freq in trs_h.items()]
        tr3_prob[k].sort()
        tr3_prob[k].reverse()

    pprint(tr3_prob)
