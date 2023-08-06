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

# Dieses Skript übersetzt tag strings der Form

# tag:url,yyyy:name

# zu Objekten der Form (YAML-notiert): 

# tag: 
#       Jahr: yyyy
#       URL: url
#       Name: Name

"""Read a tag and return a dict with the
tags information."""

class tag_zu_objekt: 
        """Read a tag and return a dict with the
tags information."""
        def __init__(self, tag): 
                self.tag = tag
        def tag_objekt(self):
                
                # Erstmal definieren wir Grundformate. 
                FORMAT_JAHR = 'yyyy'
                FORMAT_TAG = 'tag:'
                # Und deren Längen. 
                length_yyyy = len(FORMAT_JAHR)
                length_tag = len(FORMAT_TAG)
                
                # Danach schmeißen wir den Prefix raus:'t ag:'
                zwischenstring = self.tag[length_tag:]
                # Dann müssen wir in der Lage sein den String zu teilen. 
                # Dafür suchen wir erstmal das Komma im String
                ort_des_kommas = zwischenstring.find(',')
                # Um Fehler auszuschließen, prüfen wir noch, ob mehr als ein Komma im tag vorkommt. TODO: Sauber schreiben! 
                anzahl_der_kommata = zwischenstring.count( ',' )
                if anzahl_der_kommata > 1: 
                        print 'Meldung: Mehr als ein Komma im Tag! Prüfen!'
                else: #print 'Meldung: Nur ein Komma im Tag. Alles OK'
                    pass 
                # Jetzt definieren wir uns die Funktion, 
                # die aus dem String ein Objekt macht. 
                URL = zwischenstring[:ort_des_kommas]
                Jahr = zwischenstring[ort_des_kommas + 1:ort_des_kommas + length_yyyy + 1] 
                Name = zwischenstring[ort_des_kommas + length_yyyy + 2:]
                tag_dict = {}
                tag_dict['URL'] = URL
                tag_dict['Jahr'] = Jahr
                tag_dict['Name'] = Name
                return tag_dict

# und rufen sie auf. 
