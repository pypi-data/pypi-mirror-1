#!/usr/bin/env python
#encoding: utf-8

# First make sure the user has at least Python 2.5
from sys import version_info
if version_info < (2,5): 
    print "The TextRPG requires at least Python version 2.5."
    print "You should easily find a current version for your system at "
    print "- http://python.org "
    exit()
elif version_info >= (3,0): 
    print "The TextRPG isn't yet ported to Python version 3 or higher."
    print "Please bare with us, or help us updating the code."
    print "- http://rpg-1d6.sf.net"
    exit()

from lib.textrpg import story

# Idee: Den Nutzer die Möglichkeiten gleich testen lassen. 
from subprocess import call 

story("""You can directly try the commands you learn in this tutorial 
using the included python interpreter. 

It will be opened for you automatically after each section. 
To leave it, just press control-D (hold the control key and press D)

Now entering the Python interpreter. 
First step: Try leaving it with control-D. 
""")

call("python")

story("Next step.")
