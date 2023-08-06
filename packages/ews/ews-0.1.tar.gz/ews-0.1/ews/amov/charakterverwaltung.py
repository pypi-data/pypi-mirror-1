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

### Imports ###

# Wir brauchen die Klasse Charakter
import Charakter

# Für die Übersetzung von IDs in Dateinamen brauchen wir noch tag_zu_datei
from Skripte.Kernskripte.ein_und_ausgabe import tag_zu_datei

# Um Charaktere per Kommandozeile übergeben zu können brauchen wir sys
import sys

# Außerdem Wollen wir einfach die neuste Version anfragen können. 
import Versionsverwaltung


### Imports ###


### Klassen ###

class Verwaltung: 
    """Manage Data-Objects. Input are the tag and the Kategorie."""
    def __init__(self, tag=u"tag:draketo.de,2007:Sskreszta", kategorie=u"Charaktere"): 
        self.tag = tag
        self.kategorie = kategorie
        #: the ID of the most recent Version. 
        self.neuste_version = self.neuste_version() 
    def neuste_version(self): 
        """return the ID of the most recent Version."""
        versionsverwaltung = Versionsverwaltung
        versionen = versionsverwaltung.Versionen(tag=tag, kategorie=u"Charaktere")
        ID = versionen.neuste #: The ID to retrieve the file.
        return ID

### Klassen ###


### User Input ###

# Das Skript muss wie folgt aufgerufen werden: 
# python charakterverwaltung.py <Kategorie> <Name> <Version> <URL> <Jahr>

try: 
    Kategorie = sys.argv[1]
    Name = sys.argv[2]
    Jahr = sys.argv[5]
    URL = sys.argv[4]
    Version = sys.argv[3]
    
    yaml_id = "ID: tag:" + URL + "," + Jahr + ":" + Name + "\n" + "Version: " + Version + "\n" + "Kategorie: " + Kategorie
    print yaml_id
    tag = "tag:" + URL + "," + Jahr + ":" + Name
    print tag
except: 
    print "Keine Kommandozeilenargumente. Verwende Standard: Sskreszta"
    yaml_id = """ID: tag:draketo.de,2007:Sskreszta
Version: 0.15
Kategorie: Charaktere
"""
    tag = "tag:draketo.de,2007:Sskreszta"

### User Input ###


### Testen ### 


verwaltung = Verwaltung(tag, u"Charaktere")

ID = verwaltung.neuste_version


charakter = Charakter.Charakter(ID)

print u'Wir haben den/die', charakter.kategorie, u'"' + charakter.name + u'" gelesen.'

char_kampfwerte = charakter.kampfwerte

print "Für das Schlachtfeld: ", char_kampfwerte

try: 
    for wert in char_kampfwerte: 
        print wert + ":", char_kampfwerte[wert]
    
    char_hauptwaffe = char_kampfwerte[u"Hauptwaffe"]
    print "\nHauptwaffe:"
    for wert in char_hauptwaffe[u"Waffe"]: 
        print wert + ":", char_hauptwaffe[u"Waffe"][wert]
    
    char_kampffertigkeit = char_hauptwaffe[u"Kampffertigkeit"]
    
    print u"Kampffertigkeit:", char_kampffertigkeit[u"Zahlenwert"]
except: 
    print "Keine Kampfwerte"

### Testen ###

## Jetzt definieren wie den Namen des Charakters
## wie er im Programm verwendet wird. 
## TODO: Beliebig viele Charakternamen 
## akzeptieren. Aktuell geht nur einer. 


#print "Öffne den Charakter " + argv[1]
#char_name = argv[1]

## Daraus erstellen wir den Dateinamen für diesen
## Charakter. 

#char_datei = char_name + "/" + char_name + ".yml"

## Danach definieren wir ein Objekt zum 
## Auslesen der Datei. 
## Achtung! Diese Objekte müssen neu instanziiert
## werden, wenn ich die Datei erneut lesen will. 

#char_auslesen = file(char_datei, 'r')

## Nun lesen wir den Charakter in einen String
## und schließen die Datei. 

#charakter_datei = char_auslesen.read()
#char_auslesen.close()


## Und übersetzen ihn mit YAML 
## in ein Python Objekt
## Das wird unser Grundlegendes Objekt werden. 

#charakter = yaml.load(charakter_datei)

## Jetzt öffnen wir eine temporäre Datei zum
## schreiben. 

#char_ausgeben = file(char_datei + '.tmp', 'w')

## schreiben den Charakter

#char_ausgeben.write(yaml.dump(charakter, default_flow_style=False, allow_unicode=True, indent=2))

## und schließen sie gleich wieder. 

#char_ausgeben.close()

## Da der Test hoffentlich geklappt hat, 
## speichern wir zum Abschluss des Programmes in 
## der Originaldatei. 

#char_speichern = file(char_datei, 'w')

#char_speichern.write(yaml.dump(charakter, default_flow_style=False, allow_unicode=True, indent=2))

#char_speichern.close()

## Abschlussbemerkung

#print "Die Bearbeitung von " + charakter[0]["Name"] + " aus der Kampagne " + charakter[2]["Grunddaten"]["Chronik"] + " ist abgeschlossen."

## print "Die gespeicherten Daten sind: "
## print yaml.dump(charakter, default_flow_style=False)
