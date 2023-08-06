#!/bin/env python
# This Python file uses the following encoding=utf-8

# Amo - Allgemeine Modulare Objektverwaltung im lesbaren YAML Format
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

# Dieses Skript übersetzt tag-IDs zu Dateien. 

# Als Eingabe erhalten wir eine tag-ID im Format
# tag:url,yyyy:name
# eine Version und eine Kategorie
# Als Ausgabe wollen wir eine Datei-Adresse im Format
# Kategorie/name-version-yyyy-url.yml

"""Read an input-object ('ID' supplies the tag) and translate it to a file-path"""
from os.path import join
import tag_zu_objekt
import tag_zu_datei_von_tag

class Datei: 
        """Read a tag and return a
corresponding file-name"""
        def __init__(self, Eingabe, speicherordner_rel_zu_home=".amov"): 
                self.Eingabe = Eingabe
                self.tag_string = self.Eingabe["ID"]
                self.version = self.Eingabe["Version"]
                self.speicherordner_rel_zu_home = speicherordner_rel_zu_home
                self.basisordner = join(tag_zu_datei_von_tag.BASISORDNER, speicherordner_rel_zu_home)
                # wir holen uns das Objekt das dem tag entspricht.
                self.tag_zum_objekt = tag_zu_objekt.tag_zu_objekt(self.tag_string)
                self.tag_objekt = self.tag_zum_objekt.tag_objekt()

        def dateipfad(self): 
            return join(self.basisordner, self.kategorie)
        
        def dateiname_ausgeben(self): 
                # Mit dem Tag_objekt und dem Eingabe-Wörterbuch können wir nun den Datei-String erzeugen. 
                tag_zu_dat_v_t = tag_zu_datei_von_tag.Datei(tag=self.tag_string, kategorie=self.kategorie_ausgeben(), version=self.version, speicherordner_rel_zu_home=self.speicherordner_rel_zu_home)
                datei = tag_zu_dat_v_t.dateiname_ausgeben()
                return datei
        
        def kategorie_ausgeben(self):
                return self.Eingabe['Kategorie']
                
        def name_ausgeben(self): 
                return self.tag_objekt['Name']
		
        
#### Self-Test ####

if __name__ == "__main__": 
    pass

#### Self-Test ####
