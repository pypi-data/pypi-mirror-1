#!/usr/bin/env python
# encoding: utf-8

"""The battle module provides functions for battles between more than 2 participants."""

#### CONTROL PARAMETERS ####

# BIAS

# each factor of biasfactor gives +1 to attack for superior numbers
biasfactor = 1.4

# multiplier for the bias calculation
biasmultiplier = 2.0

# the maximum biasfactor (if multiplied with biasmultiplier, approached asymptotically
biascutoff = 8

#### Imports ####

# We need the Math module for the logarithm
from math import log

def bias(size_of_group_0, size_of_group_1):
    """Return the modifier for number of fighters. 

If group 0 is bigger, the modifier is positive, if group 1 is bigger, it is negative.
"""
    if max(size_of_group_0, size_of_group_1) < 5:
        if size_of_group_0 > size_of_group_1: 
            bias = int(round(3 * float(size_of_group_0 - size_of_group_1)/max(1, size_of_group_1)))
        else: 
            bias = (-1)*int(round(3 * float(size_of_group_1 - size_of_group_0)/max(1, size_of_group_0)))
    else: 
        q = log(float(max(1, size_of_group_0))/max(1, size_of_group_1),biasfactor)
        bias = int(round(biasmultiplier * q/(1+abs(q)/biascutoff)))
    return bias
