#!/bin/env python
# encoding: utf-8
"""
Read out and write out an Object from/to a yaml-file.

This is a base class which gets used by other classes. 

Just call it with an ID-dict and a basic template (object or dict) and get the object or dict via Objekt.objekt, or write it via Objekt.write(<dict>). 

To tell it NOT to create a file, if it is missing, pass the parameter: erstellen=False
"""


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

# Diese Datei ist ein Container für die klasse Charaktere

### Imports ###

# Für das Dateiformat brauchen wir yaml, wir brauchen load udn dump
from yaml import load as yaml_load
from yaml import dump as yaml_dump

# Für die Übersetzung von IDs in Dateinamen brauchen wir noch tag_zu_datei

from ein_und_ausgabe import tag_zu_datei

# Um Charaktere per Kommandozeile übergeben zu können brauchen wir sys
import sys

# Für die Prüfung ob Charakterdateien schon existieren brauchen wir außerdem os.path

from os.path import isdir as path_isdir
from os.path import exists as path_exists

from os import makedirs

from os.path import dirname

### Imports ### 

### Classes ###

class Objekt: 
    def __init__(self, ID=yaml_load("""# tag:1w6.org,2008:ID
ID: tag:draketo.de,2007:Sskreszta
Version: 0.15
Kategorie: Charaktere
"""), template=yaml_load("""# tag:1w6.org,2008:Charakter
- Name: " "
- Grunddaten: 
    Beschreibung: " "
    Herkunft: 
        Sprache: ' '
        Region: ' '
    Stimmung: ' '
- Werte:
    - Eigenschaften: " "
    - Fertigkeiten: 
        Nahkampf: &id001
          Zahlenwert: 12
    - Merkmale: " "
- Ausrüstung: 
    Waffen:
      Waffenlos: &id002
        Name: Waffenlos
        Schaden: 1
    Rüstung: 
        Stoffkleidung: &hauptruestung
            Name: Stoffkleidung
            Schutz: 1
- Kampfwerte:  
    Hauptwaffe:
      Kampffertigkeit: *id001
      Waffe: *id002
    Trefferpunkte: 24
    Wundschwelle: 4
    Hauptrüstung: *hauptruestung"""),  erstellen=True): 
        self.ID = ID
        self.versions_tag = "tag:1w6.org,2008:Objekt"
        self.template = template
        self.erstellen = erstellen
        self.template_yaml = yaml_dump(self.template, default_flow_style=False, allow_unicode=True)
        self.objekt = self.laden()
    
    def laden(self):
        """Load an object from a yaml-file."""
        # print "Charakterbogen aus Datei", self.dateiname(), "wird geladen" 
        # Erst sicherstellen, dass alle config-ordner existieren. 
        if not path_isdir(dirname(self.dateiname())) and self.erstellen: 
            makedirs(dirname(self.dateiname()))
        
        if path_exists(self.dateiname()): 
          datei = open(self.dateiname(), "r")
          charakter = yaml_load(datei.read())
          datei.close()
          return charakter
        
        elif self.erstellen: 
          # print "Datei", self.dateiname(), "existiert nicht. Wird erstellt."
          datei = open(self.dateiname(), "w")
          datei.write(self.template_yaml)
          datei.close()
          return self.laden()
        else: 
           raise FileNotFoundException("Die Datei existiert nicht und konnte nicht erstellt werden.")
    
    def dateiname(self): 
        """Return path and filename based on Cathegory, Version and Tag."""
        tag_zu_dat = tag_zu_datei.Datei(self.ID) 
        return tag_zu_dat.dateiname_ausgeben()
    
    def kategorie(self):
        """Return the cathegory of the Object"""
        tag_zu_dat = tag_zu_datei.Datei(self.ID)
        return tag_zu_dat.kategorie_ausgeben()
    
    def write(self, neue_version=False): 
        if not neue_version: 
            # print u"öffne", self.dateiname()
            datei = open(self.dateiname(), "w")
            # print u"Schreibe", self.kategorie(), self.objekt_name()
            datei.write(self.yaml())
            datei.close()
        else: # TODO: Direkt in eine neue Version schreiben ermöglichen. 
            raise NotImplementedException("Direkt in eine neue Version schreiben ist noch nicht implementiert.")
    
    def yaml(self): 
        return "# " + self.versions_tag + "\n" + yaml_dump(self.objekt, default_flow_style=False, allow_unicode=True)
    
    def objekt_name(self): 
        tag_zu_dat = tag_zu_datei.Datei(self.ID)
        return tag_zu_dat.name_ausgeben()

### Classes ###

### Selt-Test ###

if __name__ == '__main__': 
    objekt = Objekt()
    print objekt
    print objekt.yaml()
