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

"""Manage Grammars for Name-Generation. 

This file returns a grammar-object if it is given an ID or tag. 
Useage: 

>>> grammar = Grammar(ID=None, art=type, tag="tag:1w6.org,2007:Foo")
>>> print "The Grammar is:", grammar.grammar
The Grammar is: {'nameMiddle': ['<nmCons><nmVowel>'], 'nameStart': ['<nsCons><nmVowel>', '<nsCons><nmVowel>', '<nsCons><nmVowel>', '<nsVowel>'], 'nameMiddle0to2': ['', '<nameMiddle>', '<nameMiddle><nameMiddle>'], 'name': ['<nameStart><nameMiddle0to2><nameEnd>'], 'neVowel': ['e', 'i', 'a', 'au'], 'nmCons': ['l', 'm', 'lm', 'th', 'r', 's', 'ss', 'p', 'f', 'mb', 'b', 'lb', 'd', 'lf'], 'nsVowel': ['A', 'Au', 'Ei'], 'nsCons': ['J', 'M', 'P', 'N', 'Y', 'D', 'F'], 'nmVowel': ['a', 'e', 'i', 'o', 'u', 'au', 'oa', 'ei'], 'neCons': ['r', 'n', 'm', 's', 'y', 'l', 'th', 'b', 'lb', 'f', 'lf'], 'nameEnd': ['<neCons><neVowel>', '<neCons>', '<neCons>']}



You need either an ID or a tag. If you use a tag, you must set the ID to None, else teh default ID will be used: 

grammar = Grammar(ID=None, art=type, tag=tag)"""

### Imports ###

# Für das Dateiformat brauchen wir yaml, hier müssen wir yaml nur laden können. 
from yaml import load as yaml_load

# Um die Dateien zu laden, nutzen wir die Objekt-Klasse. 
import Skripte.Kernskripte.Objekt as Objekt

# Außerdem brauchen wir die Versionsverwaltung.
import Versionsverwaltung

### Imports ###

### Klassen ###

class Grammar: 
    def __init__(self, ID=None, art=None, tag="tag:1w6.org,2007:Foo"): 
        # If we only get a tag and no ID, use Versionsverwaltung, to create an ID from the tag.
        if ID != None: 
            self.ID = ID
        else: 
            versionen = Versionsverwaltung.Versionen(tag=tag,kategorie=u"Namensgrammatiken")
            self.ID = versionen.neuste
        #: The kind of name we want to generate. This isn't used yet.
        self.art = art
        # Utilize the Objekt coremodule to load the Grammar Object from a file via the ID. Also supply a template for the case that the file doesn't exist. 
        self.objekt = Objekt.Objekt(ID=self.ID, template=yaml_load(self.grammar_template_yaml()))
        # Get self.grammer, the content of the object which is the attribute we use for name-generation.
        self.grammar = self.objekt.objekt
    
    def grammar_template_yaml(self): 
        """Return a grammar template."""
        return """name: [<nameStart><nameMiddle0to2><nameEnd>]
nameEnd: [<neCons><neVowel>, <neCons>, <neCons>]
nameMiddle: [<nmCons><nmVowel>]
nameMiddle0to2: ['', <nameMiddle>, <nameMiddle><nameMiddle>]
nameStart: [<nsCons><nmVowel>, <nsCons><nmVowel>, <nsCons><nmVowel>, <nsVowel>]
neCons: [r, n, m, s, y, l, th, b, lb, f, lf]
neVowel: [e, i, a, au]
nmCons: [l, m, lm, th, r, s, ss, p, f, mb, b, lb, d, lf]
nmVowel: [a, e, i, o, u, au, oa, ei]
nsCons: [J, M, P, N, Y, D, F]
nsVowel: [A, Au, Ei]
"""

#### Classes ####

#### Self-Test ####

if __name__ == '__main__': 
    # Erst holen wir uns das Namensgrammatik-Modul mit Standardwerten.
    #: Das Grammatikobjekt 
    grammar = Grammar()
    # Dann geben wir dei Grammatik aus. 
    print grammar.grammar
    # Danach testen wir das Modul mittels Docstrings. (Infos im pydoc String am Anfang der Datei)
    # Dafür holen wir uns das doctest modul. 
    import doctest
    # und starten dann dessen Test. 
    doctest.testmod()

#### Self-Test ####
