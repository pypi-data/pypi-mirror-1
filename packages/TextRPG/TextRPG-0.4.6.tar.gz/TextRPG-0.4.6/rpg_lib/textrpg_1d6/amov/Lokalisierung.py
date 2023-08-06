#!/bin/env python
# encoding: utf-8

# Charakterverwaltung - Verwalte Charaktere im lesbaren YAML Format
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

"""Manage localized strings

Hier werden lokalisierte Ausgaben geladen. 

"""

### Imports ###

# Und um Grundfunktionen zu bieten, nutzen wir Object
import Object

### Imports ###

### Klassen ###

class Lokalisierung(Object.Object): 
    def __init__(self, ID=None, art=None,  tag=u"tag:1w6.org,2008:de_DE", kategorie="Text", *args, **kwds): 
        """Lokalisierung des Skriptes"""
        super(Lokalisierung, self).__init__(ID=ID, art=art, tag=tag, kategorie=kategorie, *args, **kwds)
        #: Das Charakterwörterbuch mit allen Charakterdaten aus der Datei. 
        self.locale = self.daten
    
    def basic_data_yaml(self): 
    	return """Name: de_DE
"""
            

### Self-Test ###

def _test(): 
	import doctest
	doctest.testmod()

if __name__ == "__main__": 
   _test() 

if __name__ == '__main__': 
        
        locale = Lokalisierung()
        print locale.locale
        locale.save()

### Self-Test ###
