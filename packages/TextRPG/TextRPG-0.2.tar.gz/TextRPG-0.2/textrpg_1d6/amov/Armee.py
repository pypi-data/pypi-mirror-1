#!/usr/bin/env python
# encoding: utf-8

# Armeenverwaltung - Verwalte Armeen im lesbaren YAML Format
# Copyright © 2007 - 2007 Arne Babenhauserheide

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

"""Verwalte Dateien von Armeen

Beispiel: 
>>> Schlacht = Schlacht()
>>> Schlacht.schlacht
[(('Menschen Armee', 0.5, 0.40000000000000002), [], [('tag:1w6.org,2007:Mensch', 10, -1, 'Soldat', True), ('tag:draketo.de,2007:Sskreszta', 1, -1, 'Held', False)]), (('Goblin Armee', 0.40000000000000002, 0.40000000000000002), [], [('tag:1w6.org,2007:Goblin', 15, -1, 'Soldat', True)])]

 """


### Imports ###

# Für das Dateiformat brauchen wir yaml
from yaml import load as yaml_load

# Um die Dateien zu laden, nutzen wir die Objekt-Klasse. 
import Skripte.Kernskripte.Objekt as Objekt

# Um immer die neuste Version zu haben brauchen wir die Versionsverwaltung
from Versionsverwaltung import Versionen

### Imports ###

### Klassen ###

class Armee: 
    def __init__(self, ID=None, art=None,  tag=u"tag:1w6.org,2008:Menschen",  data=None): 
        #: Der Identifikator der Armee-Datei
        if ID is not None: 
            self.ID = ID
        elif tag is not None: 
            # Wenn keine ID bekannt ist, lade die neuste Datei
            versionen = Versionen(tag=tag,  kategorie=u"Armeen")
            self.ID = versionen.neuste
        # Wenn daten angegeben werden, sollen sie in einer neuen Version gespeichert werden. 
        if data is not None: 
            self.data = data #: Neue Daten, die gespeichert werden sollen. 
            # TODO: If data is given, create a new minor version of the file. 
        
        #: Die Art des Charakters. Wird noch nicht verwendet. 
        self.art = art
        #: Das Charakterobjekt. Es bietet das dict und ein paar Methoden. 
        self.objekt = Objekt.Objekt(ID=self.ID, template=yaml_load(self.standard_schlacht_yaml()))
        #: Das Charakterwörterbuch mit allen Charakterdaten aus der Datei. 
        self.armee = self.objekt.objekt
    
    def standard_schlacht_yaml(self): 
    	return """# Battlefield definition: (armies)
    # Army definition: (army_data, [groups], [chartypes])
    # army_data definition: ('name', resignratio, fleeratio)
    # Chartype definition: ("tag", number_of_soldiers, 'group' (-1=army), 'Type_of_chars', from_template?)
!!python/tuple
  - !!python/tuple
    - Menschen Armee
    - 0.5
    - 0.40000000000000002
  - []
  - - !!python/tuple
      - tag:1w6.org,2007:Mensch
      - 10
      - -1
      - Soldat
      - true

"""
    
    

### Klassen ###

### Self-Test ###

def _test(): 
	import doctest
	doctest.testmod()

if __name__ == "__main__": 
   _test() 

if __name__ == '__main__': 
        pass

### Self-Test ###
        
