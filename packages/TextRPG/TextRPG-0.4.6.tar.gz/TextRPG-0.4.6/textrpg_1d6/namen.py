#!/bin/env python
# encoding: utf-8

# Schlachtfeld - Großkämpfe im EWS System
#   http://rpg-tools-1d6.sf.net
# Copyright © 2007 - 2007 Achim Zien

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

"""Dieses Modul kapselt mehrere Namensgeneratoren. 

Anwendung: 

import namen

name = Name(anzahl=200,  quelle="yould", art="Englisch")

Möglichkeiten: 

anzahl: yould und cfnamegen erstellen beide immer 500 namen auf einen Schlag, was bei Geschiwndigkeitstest berücksichtigt werden sollte. 

quellen: 
	- yould: Namen auf Grundlage der Wahrscheinlichkeit, dass eine bestimmte Kombination in einem Wort auftaucht. 
	- pointon_phonetic: Einfacher Namensgenerator mit zufallsalgorythmus
	- cfnamegen: Ähnlich ie pointon_phonetic. Auf Grundlage von Kontexctfreien Grammatiken 

art: Wird bisher nur von yould verwendet. Esperanto oder Enlisch. Sonstige Werte werden als "Altenglisch" gewertet (default). 

"""

#### Imports ####

import random_phonetic_name_generator_von_Pointon.random_phonetic_name_generator as phonetic_gen

import yould.yould as yould

# Get os for reading the path to the sourcefile.
from os.path import join,  dirname

import namegen.pycfnamegen.cfnamegen as cfnamegen

# Obtain Grammars from yaml-files
from amov import Namensgrammatik, Versionsverwaltung


#### Imports ####

#### Classes ####

class Name: 
    def __init__(self, art="Esperanto", familie="default", stimmung="default", anzahl=1, quelle="yould"): 
        """Container for all name-generation actions. Call it global, to be able to reuse it."""
        # TODO: Implement familie und stimmung
        self.name = "" #: One result
        self.names = [] #: The list of names.
        self.art = art #: The type of the name. Ork, Elf, Mensch, Troll, Deutsch, Englisch, ... 
        self.familie = familie #: Die Unterart. Orks -> Mordor, Orks -> Isengard, noch nicht in Verwendung
        self.stimmung = stimmung #: Stimmung: Düster, Stark, Verloren... noch nicht in Verwendug.
        self.anzahl = anzahl #: Number of names to generate. 
        self.anzahl_erzeugter_namen = 0 #: Wieviele Namen dieses Objekt bereits erzeugt hat.
        self.Quelle = quelle #: Die genutzte Namensquelle.
        
    def erzeuge(self,art="Esperanto", familie="default", stimmung="default"): 
        """Erzeuge die Namen. After 2500 names, always switch to the quick gen."""
        # Wenn diese Funktion mit veränderter Namensart aufgerufen wird, muss die Namensliste geleert werden. 
        if self.art != art: 
            self.names = []
            self.art = art
        if self.anzahl_erzeugter_namen < 4500: 
            self.schnell = False
        else: 
            self.schnell = True
        
        if self.Quelle == "pointon_phonetic" or self.schnell: 
            return self.pointon_namen()
        elif self.Quelle == "yould": 
            return self.yould_namen(art, familie, stimmung)
        elif self.Quelle == "cfnamegen": 
            return self.cfnamegen_namen()
    
    def erzeuge_speziellen_namen(self,art="Esperanto", familie="default", stimmung="default"): 
        """Erzeuge besonderen Namen. Nimm dafür immer den besten Namensgenerator."""
        return self.yould_namen(art=art, familie=familie, stimmung=stimmung)
        
    def yould_namen(self, art="Esperanto", familie="default", stimmung="default"): 
        """Hol die Namen aus dem Yould Namensgegerator."""
        if self.anzahl == 1: # Generate only one name
            # since yould is much faster when it generates many names at once, we first prepare 1000 names for internal use.
            # But only, if we have no more names avaible. 
            if len(self.names) < 2: 
                # print "Erzeuge die Namen", self.anzahl_erzeugter_namen, 'bis',  self.anzahl_erzeugter_namen + 500
                self.names = self.yould_aufrufen(anzahl=100, art=art, familie=familie, stimmung=stimmung)
                self.anzahl_erzeugter_namen += 50
            self.name = " ".join([self.names[0].capitalize(), self.names[1].capitalize()])
            # Lösche die beiden verwendeten Namen.
            del(self.names[0])
            del(self.names[0])
            # print self.name, "noch", len(self.names), "Namen verfügbar"
            return self.name
        else: # Generate many names
            self.names = self.yould_aufrufen(self.anzahl * 2, art=art, familie=familie, stimmung=stimmung)
            names = []
            for i in range(self.anzahl): 
                names.append(self.names[2*i].capitalize() + " " + self.names[(2*i)+1].capitalize())
            return names
            
    def yould_aufrufen(self, anzahl=1000, art="Esperanto", familie="default", stimmung="default"): 
        if art == "Esperanto": 
            names = yould.generate_names(eval(open(join(dirname(__file__), "yould/gutenberg_esperanto2.prob")).read()), 5, 12, 1000, 0, min_prob=0.000000001, max_prob=0.00001) # TODO: Get the path to the your dir dynamically, independent of the calling script. 
        elif art == "Englisch": 
            names = yould.generate_names(eval(open(join(dirname(__file__), "yould/various_gutenberg.prob")).read()), 5, 12, 1000, 0, min_prob=0.000000001, max_prob=0.00001)
        else: 
            names = yould.generate_names(eval(open(join(dirname(__file__), "yould/gutenberg_erotik_und_romantik.prob")).read()), 5, 12, 1000, 0, min_prob=0.000000001, max_prob=0.00001)
        return names
    
    def pointon_namen(self): 
        """Hol die Namen aus dem Pointon Namensgenertor."""
        if self.anzahl == 1: 
            self.name = phonetic_gen.namegen() + " " + phonetic_gen.namegen()
            return self.name
        else: 
            while self.anzahl > 0: 
                self.name = phonetic_gen.namegen() + " " + phonetic_gen.namegen()
                self.names.append(self.name)
                self.anzahl -= 1
            return self.names
            
    def cfnamegen_namen(self): 
        """Hol die Namen aus dem CFNameGen Namensgenertor."""
        if self.anzahl == 1: 
            # Fist create 1000 names and keep them (optimization). 
            if len(self.names) == 0 or len(self.names) == 1: 
                self.names =  self.cfnamegen_aufrufen(anzahl=1000)
            # Then for each name join two names to get first and second name. 
            self.name = self.names[0] + " " + self.names[1]
            del self.names[0]
            del self.names[0]
            return self.name
        else: 
            # return a fixed number of names.
            grammatikObjekt = Namensgrammatik.Grammar()
            fooGrammar = grammatikObjekt.grammar
            names = []
            self.names = self.cfnamegen_aufrufen(anzahl=self.anzahl*2)
            while self.anzahl != 0: 
                self.name = self.names[0] + " " + self.names[1]
                del self.names[0]
                del self.names[0]
                names.append(self.name)
                self.anzahl -= 1
            return names
        
    def cfnamegen_aufrufen(self, anzahl=1000): 
        grammatikObjekt = Namensgrammatik.Grammar()
        fooGrammar = grammatikObjekt.grammar
        foong = cfnamegen.CFNameGen(fooGrammar)
        names = []
        while anzahl != 0: 
            names.append(foong.getName())
            anzahl -= 1
        return names

        

#### Classes ####

#### Self-Test ####

if __name__ == "__main__": 
    print "Erzeuge Esperanto-Namen mit yould"
    name = Name(anzahl=20,  quelle="yould")
    namen = name.erzeuge()
    for i in namen: 
        print i
    print "\nErzeuge Englische Namen mit yould"
    name = Name(anzahl=20,  quelle="yould", art="Englisch")
    namen = name.erzeuge()
    for i in namen: 
        print i
    print "\nErzeuge erotische Namen mit yould"
    name = Name(anzahl=20,  quelle="yould", art="Martin Luther")
    namen = name.erzeuge()
    for i in namen: 
        print i
    print "\nErzeuge die Namen mit pointon"
    name = Name(anzahl=20,  quelle="pointon_phonetic")
    namen = name.erzeuge()
    for i in namen: 
        print i
    print "\nErzeuge die Namen mit cfnamegen"
    name = Name(anzahl=20,  quelle="cfnamegen")
    namen = name.erzeuge()
    for i in namen: 
        print i

#### Self-Test ####
