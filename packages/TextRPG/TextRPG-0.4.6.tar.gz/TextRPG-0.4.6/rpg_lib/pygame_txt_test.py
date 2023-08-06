from pygame_rpg import *
while True:
    for i in "xsdgndfjcfc":
        if i == "x":
            txt = i
        else:
            txt += i
    text, tR = fungus_text(txt)
    if (text, tR) in stuff:
        stuff.remove((text, tR))
    stuff.append((text, tR))
    sleep(0.3)
    

