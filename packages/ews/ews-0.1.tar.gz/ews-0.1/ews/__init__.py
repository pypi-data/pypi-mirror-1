#!/usr/bin/env python
# encoding: utf-8

# EWS - An RPG backend module providing character management and interaction. 
# 
# Copyright © 2008 Arne Babenhauserheide
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

"""The ews ("Ein Wuerfel Sytem" is german for "One Die System") is a free rpg backend which covers char interaction and char management -> http://1w6.org. 

Chars have attributes, abilities, edges/flaws, equipment and battle values (directly derived from the attributes and abilities). 


Usage from command line: 

    - None yet. 


Examples: 

    - None yet. 


Use-Cases: 

 - Creating Chars
    
    Create and print a char from a tag-string
        >>> from ews import Char
        >>> tag_string = "tag:1w6.org,2008:Human"
        >>> char_from_tag = Char(source=tag_string, template=False) 
    
    template=False says: Go with the name inside the stored file or (if None is avaible) in the tagstring. 
    
    Else it would create a new name for it. 
    
    TODO: Change the default to template=False (some checking of other libs necessary for that)
        >>> print char_from_tag
        Name: Human
        Sprache: Esperanto
    
    TODO: Create a char from a char dict. 
    
    
 - Combat
    
    Create two chars and let them fight one round. 
        >>> char1 = Char()
        >>> char2 = Char()
        >>> print char1.wounds, char2.wounds
        [0, 0] [0, 0]
        >>> char1.fight_round(char2)
        >>> result = (char1.get_battle_result_values(), char2.get_battle_result_values())  
        >>> # Gives TP and wounds for Char 1 and 2
    
    Let the two chars fight a battle with the one roll battle system. 
        >>> char1.fight_one_roll_battle(char2)
        >>> result = (char1.get_battle_result_values(), char2.get_battle_result_values()) 
        >>> # Dict for char1 and for char 2
    
    TODO: Fight a whole battle with the complex battle system. 
    
    
 - Attributes
    
    List all attributes. If the char has None, print a single space. 
        >>> char1.attributes
        ' '
    
    
 - Skills and checks
    
    List all skills. If the char has None, print a single space. 
        >>> char1.skills
        {'Nahkampf': {'Grundwert': 12, 'Striche': 3, 'Zahlenwert': 12}}
    
    Do a skill test (default target number is 9)
        >>> print "Do we manage to cook a nice meal?"
        Do we manage to cook a nice meal?
        >>> result = char1.check_skill("cook")
    
    Do a skill test against another target number. 
        >>> print "Do we manage to cook an exceptional meal?"
        Do we manage to cook an exceptional meal?
        >>> result = char1.check_skill("cook", MW=18)
    
    TODO: Check how good we manage something. 
    
    TODO: Check if we manage to make a roll and how good we manage it. 
    
    
 - Competition (skill vs. skill and similar)
    
    TODO: Let two chars compete for one round. 
    
    TODO: Let two chars do a full competition. 
    
    
 - Equipment
    
    Get the current equipment of the char. 
        >>> for i in char1.equipment: print char1.equipment[i] 
        {'Stoffkleidung': {'Name': 'Stoffkleidung', 'Schutz': 1}}
        {'Waffenlos': {'Name': 'Waffenlos', 'Schaden': 1}}
        >>> # TODO: Fix to make it nicer to use. 
    
    
    Get the current combat equipment of the char (armor and weapon). 
        >>> char1.weapon
        {'Name': 'Waffenlos', 'Schaden': 1}
        >>> char1.armor
        {'Name': 'Stoffkleidung', 'Schutz': 1}
    
    TODO: Change armor and weapon (and weapon skill). 
    
    TODO: Get the current clothes of the char. 
    
    TODO: Change the current clothes of the char. 
    
    
 - Improving Chars
    
    Improve a char by a 3 points at random (about the value to get for one gaming session in a hreo setting). 
        >>> char1.upgrade(3)
    
    Upgrade with a weighted list of attributes and skills which could be improved additionally to known skills and attributes. 
        >>> char1.upgrade(3, object=("weighted", [("attribute",  "sensitivity", 1), ("skill", "cooking", 2)]))
    
    Upgrade a specific skill or attribute. 
        >>> char1.upgrade(3, object=("skill", "talking senslessly"))
    
    
 - Saving Chars
    
    Save the changed (wounded but improved) Char as new template. 
    
    Commented out, because this creates new files. 
        >>> # char1.name = char1.amov.tagname
        >>> # char1.save()
    
    Save the changed Char as a new char and get the new tag to call it again. 
    
    Commented out, because this creates new files. 
        >>> # tagstring = char1.amov.tagstring_without_name + char1.name # The tag to call the char
        >>> # char1.save()
        >>> # char1_again = Char(source=tagstring, template=False)
    
    
 - Finishing Chars off :) 
    
    And in the end: Die 
        >>> char1.die()
    
    
Source URL (Mercurial): U{http://rpg-1d6.sf.net/hg/1d6}

PyPI URL: U{http://pypi.python.org/pypi/ews}
"""

#### Package information ###

__version__ = "0.1"

#### Package information ###

#### Imports ####

from char import Char

#### Imports ####

#### Self-Test ####

def _test():
    """Launch the doctests."""
    from doctest import testmod
    testmod()

if __name__ == "__main__": 
    _test()
