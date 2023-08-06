#!/usr/bin/env python
# encoding: utf-8
"""A branching story: moving through the woods.

decisions: right, left, straight, back

ideas: 
    - with a pursuer

"""
from rpg_lib.textrpg import story, ask, _

# Only speak the into, if called directly. 
if __name__ == "__main__": 
    story("""Fading red light 
filters through the leaves 
and trunks of the trees, 
as you leave the campsite. 

The first chill of the night 
touches your skin, 
and your summercoat
thin as it is, 
protects you just feebly. 

But the way which was clear 
the day before today
now seems forgotten, 
after this day of dancing
with the sister of the sun, 
a child of the faery kin. 
""")

wood = [
['your car',   'withered leaves', 	0,			            0, 	0], 
[0, 	       'the rabbit hill', 	'the dark underbrush', 	0, 	0], 
[0,     	   'the angry boar', 	'the campsite', 	    0, 	0], 
[0, 	       	0, 			         0, 			        0, 	0], 
[0, 	       	0, 			         0, 			        0, 	0]
]

location_descriptions = {
'your car': """
You reach your car and leave the woods, 
but a memory of old trees, dark shadows and wonder remains.
""", 

'the angry boar': """
As you enter a darker region of the woods, you hear the rustling of leaves behind you. 
Minutes later, you still don't quite know, how you escaped, 
but the boar doesn't follow you anymore. 
"""
}
# TODO: Write text for all locations. 

class Path(object):
    """Moving through a maze. """
    def __init__(self, start=(2, 2), target = (0,0), maze = wood, descriptions = location_descriptions, description_type = "text", story=story, ask=ask):
        """
        @param start: Where we begin. 
        @type start: Tuple
        
        @param target: Where we want to get. 
        @type target: Tuple
        
        @param maze: The maze in which we move. 
        @type maze: List of Lists
        
        @param descriptions: Descriptions for the places in the maze. 
        @type start: Dictionary
        
        @param story: The function for telling stories. 
        @type story: Function
        
        @param ask: The function to ask the user. 
        @type ask: Function
        """
        #: Where we are
        self.position = start
        #: Where we want to get
        self.target = target
        #: The terrain / maze
        self.maze = maze
        #: Descriptions for the places in the terrain / maze
        self.descriptions = descriptions
        #: The type of description. Could also be functions which get called, turning this into a quite complex adventure. 
        self.description_type = description_type
        #: The function to use for telling stories
        self.story = story
        #: The function to use for talking to the user. 
        self.ask = ask
    def pos_to_name(self, pos=(2, 2)):
        """return the location name for a position."""
        return self.maze[pos[1]][pos[0]]
    def describe(self, name):
        """Get the text for each locations name"""
        if self.description_type == "text": 
            if name in self.descriptions: 
                self.story(self.descriptions[name])
                return 
        # If we find no descriptions, just return the name. 
        self.story(name)
    def move(self):
        x, y = self.position
        # specify possible movement. 
        directions = {
        'north': (x, y - 1), # up
        'south': (x, y + 1), # down
        'west': (x - 1, y),  # left
        'east': (x + 1, y)  # right
        }
        question = _('Where do you want to go?') + ' ('
        answers = []
        # get all possible answers by checking if the ways are possible. 
        for i, j in directions.items():
            if self.maze[j[1]][j[0]]:
                answers.append(i)
        question = " ".join([question] + answers + [")"])
        description = "\n".join(['to the ' + i + ' you see ' + 
self.pos_to_name(directions[i]) for i in answers])
        self.story(description)
        target = ""
        # Ask the user until he/she supplies a valid answer. 
        while not target:  
            self.story("", autoscroll=True)
            ans = self.ask(question).strip() # removing any whitespace before the first letter
            # the users input fits any of the answers 
            # of the name of teh region for that answer, 
            # Pick that as target. 
            for i in answers: 
                name = self.maze[directions[i][1]][directions[i][0]]
                if ans.lower() in [i.lower(), i.lower()[0], name, " ".join(name.split()[1:])]: 
                    target = directions[i]
        self.position = target
        self.story("""You go to """ + self.pos_to_name(self.position))
        self.describe(self.pos_to_name(self.position))


### Usage ###

if __name__ == "__main__": 
# Get the path to move in. 
    path = Path(    start=(2,2), # Where we begin. 
                    target=(0,0), # Where the maze ends. 
                    maze=wood, # The maze in which we move
                    descriptions=location_descriptions, # Descriptions for the named locations in the maze. 
                    description_type = "text", # The maze descriptions are simple text strings. 
                    story=story, # The function for telling things to the user. 
                    ask=ask # the function for asking the user. 
                    )
    
    # Move until we reach the target. 
    while not path.position == path.target:
        path.move()
