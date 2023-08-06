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

"""Manage Charakter-Objects. 

Diese Datei ist ein Container für die klasse Charaktere. 

Aufrufen mit ID-Objekt oder tag-string. 

Beispiel: 
>>> Sskreszta = Charakter(tag=u"tag:draketo.de,2007:Sskreszta")
>>> Sskreszta.name
'Sskreszta'

ToDo: Größere Teile des Charaktersnicht mehr als attribut des OBjekts doppelspeichern, sondern nur durch Funktionen aufrufen. Das dict sollte nur einmal echt geladen werden. Die Eigenschaften des Charakters sollten mit Funktionen aus diesem Hauptdict herausgezogen werden. 
Ausgenommen davon sind Werrte, sie sehr oft gebraucht und geänbdert werden (Geschwindkeit statt Ram-Verbrauch). 
Aktuell wird er Charakter in etwa doppelt geladen.
 
 #TODO: Sourcefile dir hinzufügen. """

### Imports ###

# Um die Dateien zu laden, nutzen wir die Objekt-Klasse. 
import Skripte.Kernskripte.Objekt as Objekt

# Und wir brauchen die Basisklasse: Object
from Object import Object, _

# Um immer die neuste Version zu haben brauchen wir die Versionsverwaltung
from Versionsverwaltung import Versionen

### Imports ###

### Klassen ###

class Charakter(Object): 
    def __init__(self, ID=None, art=None,  tag=u"tag:draketo.de,2007:Sskreszta", kategorie="Charaktere", *args, **kwds): 
        super(Charakter, self).__init__(ID=ID, art=art,  tag=tag, kategorie=kategorie, *args, **kwds)
        self.beschreibung = self.ladeBeschreibung()
        self.werte = self.ladeWerte()
        self.eigenschaften = self.ladeEigenschaften()
        self.fertigkeiten = self.ladeFertigkeiten()
        self.kampfwerte = self.ladeKampfwerte()
        self.ausruestung = self.ladeAusruestung()
        self.schutz = self.ladeSchutz()
        self.herkunft = self.ladeHerkunft()
        self.sprache = self.ladeSprache()
        self.region = self.ladeRegion()
        self.stimmung = self.ladeStimmung()
        self.kategorie = self.objekt.kategorie
        # del self.daten # Wir müssen dieses Wörterbuch nicht löschen, 
        # da Python es zu cachen scheint, so dass wir dadurch kein Ram sparen. 
        # Vielleicht existiert es auch nur als symbolischer Link. 
            
    def ladeName(self): 
        """Lade den Namen des Charakters. 
        
        Wenn der Charakter keinen Namen hat, dann erzeuge einen zufälligen."""
        if self.daten[0][_(u"Name")] == " ": 
            self.daten[0][_(u"Name")] = self.objekt.objekt_name()
            self.objekt.write()
        return self.daten[0][_(u"Name")]
        
    def ladeGrunddaten(self): 
        """Lade die Grundlegenden Daten des Charakters, wie seine Beschreibung oder Herkunft. 
        
        Grunddaten enthalten im allgemeinen keine würfelrelevanten Werte."""
        return self.daten[1][_(u"Grunddaten")]
    
    # Daten laden
    def ladeKampfwerte(self): 
        """Lade die Kampfrelevanten Werte des Charakters."""
        return self.daten[4][_(u"Kampfwerte")]
    def ladeAusruestung(self): 
        """Lade die Ausrüstung des Charakters."""
        return self.daten[3][_(u"Ausrüstung")]
    def ladeBeschreibung(self): 
        return self.ladeGrunddaten()[_(u"Beschreibung")]
    def ladeHerkunft(self): 
        return self.ladeGrunddaten()[_(u"Herkunft")]
    def ladeRegion(self): 
        return self.herkunft[_(u"Region")]
    def ladeSprache(self): 
        return self.herkunft[_(u"Sprache")]
    def ladeStimmung(self): 
        return self.ladeGrunddaten()[_(u"Stimmung")]
    def ladeWerte(self): 
        return self.daten[2][_(u"Werte")]
    def ladeEigenschaften(self): 
        return self.werte[0][_(u"Eigenschaften")]
    def ladeFertigkeiten(self): 
        return self.werte[1][_(u"Fertigkeiten")]
    def ladeSchutz(self): 
        return self.kampfwerte[_(u"Hauptrüstung")][_("Schutz")]
    
    # Daten in das dict speichern
    # Das ist nötig, weil sonst beim umschreiben der Attribute des charakter-objekts das strings im dict nicht geändert wird (nur die Attribute werden umgeleitet - Strings sind nicht mutable. 
    def speichereKampfwerte(self, daten): 
        """Speichere die Kampfrelevanten Werte des Charakters."""
        self.daten[4][_(u"Kampfwerte")] = daten
    def speichereAusruestung(self, daten): 
        """Speichere die Ausrüstung des Charakters."""
        self.daten[3][_(u"Ausrüstung")] = daten
    def speichereBeschreibung(self, daten): 
        self.ladeGrunddaten()[_(u"Beschreibung")] = daten
    def speichereHerkunft(self, daten): 
        self.ladeGrunddaten()[_(u"Herkunft")] = daten
    def speichereRegion(self, daten): 
        self.herkunft[_(u"Region")] = daten
    def speichereSprache(self, daten): 
        self.herkunft[_(u"Sprache")] = daten
    def speichereStimmung(self, daten): 
        self.ladeGrunddaten()[_(u"Stimmung")] = daten
    def speichereWerte(self, daten): 
        self.daten[2][_(u"Werte")] = daten
    def speichereEigenschaften(self, daten): 
        self.werte[0][_(u"Eigenschaften")] = daten
    def speichereFertigkeiten(self, daten): 
        self.werte[1][_(u"Fertigkeiten")] = daten
    def speichereSchutz(self, daten): 
        self.kampfwerte[_(u"Hauptrüstung")][_("Schutz")] = daten
    def speichereName(self, daten): 
        self.daten[0][_("Name")] = daten
    
    def basic_data_yaml(self):
        return self.leerer_charakterbogen_yaml()
    
    def leerer_charakterbogen_yaml(self): 
        """@return: Den grundlegenden Charakterbogen. 
        
        Ideen: 
            - Immer das letzte Element in der Liste kann für Daten des Programms aufbehalten werden. 
        """
        
    	return """- Name: " "
- Grunddaten: 
    Beschreibung: " "
    Herkunft: 
        Sprache: Esperanto
        Region: " "
    Stimmung: ' '
- Werte:
    - Eigenschaften: 
        Geschicklichkeit: &id003
          Zahlenwert: 13
    - Fertigkeiten: 
        Nahkampf: &id001
          Zahlenwert: 12
          Grundwert: 12
          Passende Eigenschaften: 
          - *id003
    - Berufe: 
        Mensch: 
            Zahlenwert: 9
            Grundwert: 9
    - Merkmale: {}
- Ausrüstung: 
    Waffen:
      Waffenlos: &id002
        Name: Iron knuckles
        Schaden: 1
    Rüestung: 
        Stoffkleidung: &hauptruestung
            Name: Simple garb
            Schutz: 1
- Kampfwerte:  
    Hauptwaffe:
      Kampffertigkeit: *id001
      Waffe: *id002
    Trefferpunkte: 24
    Wundschwelle: 4
    Wunden: 
        körperlich tief: 0
        körperlich kritisch: 0
    Hauptrüstung: *hauptruestung
"""
    
    def save(self, name=None): 
        """Save the character into a file with its name. If the file already exists, increment the minor version number. 
        
        @param name: The name of the char (to call this function from outside - from ews).
        @type name: String """
        # raise NotImplementedException("Not yet implemented")
        # Get the name of the loaded char or template
        tagname = self.ID[_(u"ID")][self.ID[_(u"ID")].index(":", 4) + 1:]
        
        # If the name changed - self.name is the saved chars name, tagname is the name stored in the tag, name is the parameter passed to this function
        if name is not None and name != tagname or tagname != self.name: 
            # change the tag-line. 
            # if name was given, use it. comparing to None is the fastest, so we do that first. 
            if name is not None: 
                self.ID[_(u"ID")] = self.ID[_(u"ID")][:self.ID[_(u"ID")].index(":", 4) + 1] + name
            else: # name is None, self.name doesn't equal tagname
                self.ID[_(u"ID")] = self.ID[_(u"ID")][:self.ID[_(u"ID")].index(":", 4) + 1] + self.name
        
        # Now the tagline in the ID changed. 
        
        # First get the new ID
        # self.ID ist die alte ID
        # Use Versionsverwaltung to get a version object
        versionen = Versionen(tag=self.ID[_(u"ID")], kategorie=self.ID[_(u"Kategorie")])
        # Now call the version object to get the ID with a version chiw is increased by one. 
        self.ID = versionen.version_minor_eins_hoeher()
        
        # Now change the basic dict below the attributes. 
        
        self.speichereKampfwerte(self.kampfwerte)
        self.speichereAusruestung(self.ausruestung)
        self.speichereBeschreibung(self.beschreibung)
        self.speichereHerkunft(self.herkunft)
        self.speichereRegion(self.region)
        self.speichereSprache(self.sprache)
        self.speichereStimmung(self.stimmung)
        self.speichereWerte(self.werte)
        self.speichereEigenschaften(self.eigenschaften)
        self.speichereFertigkeiten(self.fertigkeiten)
        self.speichereSchutz(self.schutz)
        self.speichereName(self.name)
        
        # Now load and save the object at the same time. 
        self.objekt = Objekt.Objekt(ID=self.ID, template=self.daten)
        # TODO: Implement save chars - add name to tag, if it changed (i.e. if the char is called as template)
    

### Klassen ###


### Self-Test ###

def _test(): 
	import doctest
	doctest.testmod()

if __name__ == "__main__": 
   _test() 

if __name__ == '__main__': 
        charakter = Charakter()
        print 'Name:', charakter.name
        print 'Art:', charakter.art
        print '\nID:'
        for i in charakter.ID: 
            print '-', i + ':', charakter.ID[i]
        #print 'Objekt:', charakter.objekt
        #print 'Charakter:', charakter.charakter
        #print 'Grunddaten:', charakter.grunddaten
        #print 'Werte:', charakter.werte
        print '\nEigenschaften:'
        for i in charakter.eigenschaften: 
            print '-', i + ':', charakter.eigenschaften[i]
        print '\nFertigkeiten:'
        for i in charakter.fertigkeiten: 
            print '-', i + ':', charakter.fertigkeiten[i]
        print '\nKampfwerte:'
        for i in charakter.kampfwerte: 
            print '-', i + ':', charakter.kampfwerte[i]
        print '- Schutz:', charakter.schutz
        print '\nBeschreibung:', charakter.beschreibung
        print 'Herkunft:', charakter.herkunft
        print 'Sprache:', charakter.sprache
        print 'Region:', charakter.region
        print 'Stimmung:', charakter.stimmung
        print 'Kategorie:', charakter.kategorie
        
        # Test saving
        # First change the Beschreibung
        charakter.beschreibung += ". Zusatz 1."
        print charakter.charakter
        # Save the character with an incremented minor version
        charakter.save()

### Self-Test ###
