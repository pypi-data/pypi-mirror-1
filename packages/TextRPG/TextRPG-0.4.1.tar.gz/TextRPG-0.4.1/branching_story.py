"""A branching story: moving through the woods.

decisions: right, left, straight, back

ideas: 
    - with a pursuer

"""
from lib.textrpg import story, ask

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
with the sister of the sun
a child of the faery kin. 
""")

wood = [
['your car', 	'withered leaves', 	0,			0, 	0], 
[0, 		'the rabbit hill', 	'the dark underbrush', 	0, 	0], 
[0, 		'the angry boar', 	'the campsite', 	0, 	0], 
[0, 		0, 			0, 			0, 	0], 
[0, 		0, 			0, 			0, 	0]
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

def get_description(name):
    """Get the text for each locations name"""
    if name in location_descriptions: 
        return location_descriptions[name]
    else: 
        return name 

class Path(object):
    def __init__(self):
        self.position = (2, 2)
        self.target = (0, 0)
    def pos_to_name(self, pos=(2, 2)):
        """return the location name for a position."""
        return wood[pos[1]][pos[0]]
    def move(self):
        x, y = self.position
        # specify possible movement. 
        directions = {
        'north': (x, y - 1), # up
        'south': (x, y + 1), # down
        'west': (x - 1, y),  # left
        'east': (x + 1, y)  # right
        }
        question = 'Where do you want to go? ('
        answers = []
        # get all possible answers by checking if the ways are possible. 
        for i, j in directions.items():
            if wood[j[1]][j[0]]:
                answers.append(i)
        question = " ".join([question] + answers + [")"])
        description = "\n".join(['to the ' + i + ' you see ' + 
self.pos_to_name(directions[i]) for i in answers])
        story(description)
        target = ""
        while not target:  
            story("", autoscroll=True)
            ans = ask(question)
            for i in answers: 
                name = wood[directions[i][1]][directions[i][0]]
                if ans.lower() in [i.lower(), i.lower()[0], name, " ".join(name.split()[1:])]: 
                    target = directions[i]
        self.position = target
        story("""You go to """ + self.pos_to_name(self.position))
        story(get_description(self.pos_to_name(self.position)))

path = Path()
while not path.position == path.target:
    path.move()
