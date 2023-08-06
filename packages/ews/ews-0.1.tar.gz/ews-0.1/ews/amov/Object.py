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

# Für das Dateiformat brauchen wir yaml, in dieser Datei müssen wir sie nur laden können. 
from yaml import load as yaml_load

# Um die Dateien zu laden, nutzen wir die Objekt-Klasse. 
import Skripte.Kernskripte.Objekt as Objekt

# Um immer die neuste Version zu haben brauchen wir die Versionsverwaltung
from Versionsverwaltung import Versionen

### Imports ###

### Klassen ###

class Object(object): 
    def __init__(self, ID=None, art=None,  tag=u"tag:1w6.org,2008:de_DE", kategorie="locales", *arg, **kwds): 
        #: Der Identifikator der Charakter-Datei
        if ID is not None: 
            self.ID = ID
        elif tag is not None: 
            # Wenn keine ID bekannt ist, lade die neuste Datei
            versionen = Versionen(tag=tag,  kategorie=kategorie)
            self.ID = versionen.neuste
        # Get the name of the loaded char or template
        self.tagname = self.ID[u"ID"][self.ID[u"ID"].index(":", 4) + 1:]
        self.tagstring = self.ID[u"ID"]
        self.tagstring_without_name = self.ID[u"ID"][:self.ID[u"ID"].index(":", 4) + 1]
        #: Die Art der locale. Wird noch nicht verwendet. 
        self.art = art
        #: Das Charakterobjekt. Es bietet das dict und ein paar Methoden. 
        self.objekt = Objekt.Objekt(ID=self.ID, template=yaml_load(self.basic_data_yaml()))
        #: Das Charakterwörterbuch mit allen Charakterdaten aus der Datei. 
        self.daten = self.objekt.objekt
        #: Der Name der Datei
        self.name = self.ladeName()
    
    def basic_data_yaml(self): 
    	raise Exception("Must be implemented in subclass!")
    
    def ladeName(self): 
        """Lade den Namen des Charakters. 
        
        Wenn der Charakter keinen Namen hat, dann erzeuge einen zufälligen."""
        try: name = self.self.daten[u"Name"]
        except: 
            self.daten[u"Name"] = self.tagname
            name = self.tagname
        return name
    
    def save(self, name=None): 
        """Save the locale into a file with its name. If the file already exists, increment the minor version number. 
        
        @param name: The name of the char (to call this function from outside - from ews). 
        @type name: String """
        
        # If the name changed - self.name is the saved chars name, tagname is the name stored in the tag, name is the parameter passed to this function
        if name is not None and name != self.tagname or self.tagname != self.name: 
            # change the tag-line. 
            # if name was given, use it. comparing to None is the fastest, so we do that first. 
            if name is not None: 
                self.ID[u"ID"] = self.ID[u"ID"][:self.ID[u"ID"].index(":", 4) + 1] + name
            else: # name is None, self.name doesn't equal tagname
                self.ID[u"ID"] = self.ID[u"ID"][:self.ID[u"ID"].index(":", 4) + 1] + self.name
        
        # Now the tagline in the ID changed. 
        
        # First get the new ID
        # self.ID ist die alte ID
        # Use Versionsverwaltung to get a version object
        versionen = Versionen(tag=self.ID[u"ID"], kategorie=self.ID[u"Kategorie"])
        # Now call the version object to get the ID with a version which is increased by one. 
        self.ID = versionen.version_minor_eins_hoeher()
        
        # Now change the basic dict below the attributes. 
        
        # Now load and save the object at the same time. 
        self.objekt = Objekt.Objekt(ID=self.ID, template=self.daten)
        
    

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
