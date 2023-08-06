# pylint: disable-msg=R0904,W0142,W0511,W0104,C0321,E1103,W0212
# 
# Copyright 2008 German Aerospace Center (DLR)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


"""
Check name of new collections/resources for "illegal" characters.
"""


import re
import unicodedata

umlaute_in_unicode = [unicodedata.lookup("LATIN CAPITAL LETTER A WITH DIAERESIS"),
                      unicodedata.lookup("LATIN SMALL LETTER A WITH DIAERESIS"),
                      unicodedata.lookup("LATIN CAPITAL LETTER O WITH DIAERESIS"),
                      unicodedata.lookup("LATIN SMALL LETTER O WITH DIAERESIS"),
                      unicodedata.lookup("LATIN CAPITAL LETTER U WITH DIAERESIS"),
                      unicodedata.lookup("LATIN SMALL LETTER U WITH DIAERESIS"),
                      unicodedata.lookup("LATIN SMALL LETTER SHARP S")]
# Bemerkung:
# so geht es auch: 
# print u"\N{LATIN CAPITAL LETTER A WITH DIAERESIS}".encode("latin-1")

# Define characters and character base sets
GERMAN  = u"".join(umlaute_in_unicode)
ALPHA_NUM = "A-Za-z0-9"
ALPHA = "A-Za-z"
NUM = "0-9"
SPACE   = " "
UNDER   = "_"
DASH    = "\-"
DOT     = "\."
EXCLAM  = "\!"
TILDE   = "\~"
DOLLAR  = "\$"
COLON   = ":"

# Define character groups
LETTER_NUM = ALPHA_NUM + GERMAN
LETTER = ALPHA + GERMAN

# Define character sets for names
#FIRST_PROPERTY_CHAR= LETTER_NUM + UNDER
#FIRST_RESOURCE_CHAR= FIRST_PROPERTY_CHAR + TILDE + EXCLAM + DOLLAR
#RESOURCE_CHAR= FIRST_RESOURCE_CHAR + DASH + DOT + COLON + SPACE

FIRST_PROPERTY_CHAR = LETTER + UNDER
FIRST_RESOURCE_CHAR = FIRST_PROPERTY_CHAR + NUM + TILDE + EXCLAM + DOLLAR + DOT + DASH + COLON
PROPERTY_CHAR = FIRST_PROPERTY_CHAR + NUM + DASH + DOT
RESOURCE_CHAR = FIRST_RESOURCE_CHAR + SPACE

# Define regular expressions for name validation
PROPERTY_RE = re.compile(u"[^"+ PROPERTY_CHAR +"]")
RESOURCE_RE = re.compile(u"[^"+ RESOURCE_CHAR +"]")
PROPERTY_FIRST_RE = re.compile(u"^["+ FIRST_PROPERTY_CHAR +"]")
RESOURCE_FIRST_RE = re.compile(u"^["+ FIRST_RESOURCE_CHAR +"]")


                      
def isValidPropertyName(name):
    """
    Check if C{name} complies to L{PROPERTY_RE} and L{PROPERTY_FIRST_RE}.
    
    @param name: name of resource/collection
    @type name: unicode-string
    
    @rtype: boolean
    """
    illegalChar = PROPERTY_RE.search(name)
    return illegalChar == None  and  PROPERTY_FIRST_RE.match(name) != None
    
def isValidResourceName(name):
    """
    Check if C{name} complies to L{RESOURCE_RE} and L{RESOURCE_FIRST_RE}.
    
    @param name: name of resource/collection
    @type name: unicode-string
    
    @rtype: boolean
    """
    illegalChar = RESOURCE_RE.search(name)
    return illegalChar == None  and  RESOURCE_FIRST_RE.match(name) != None


def validatePropertyName(name):
    """
    Check if C{name} complies to L{PROPERTY_RE} and L{PROPERTY_FIRST_RE}.
    
    @param name: name of resource/collection
    @type name: unicode-string
    @raise WrongNameError: if validation fails (see L{datafinder.common.NameCheck.WrongNameError})
    """
    illegalChar = PROPERTY_RE.search(name)
    if illegalChar:
        raise WrongNameError(illegalChar.start(), name[illegalChar.start()])
    if not PROPERTY_FIRST_RE.match(name):
        if len(name) > 0:
            raise WrongNameError(0, name[0])
        else:
            raise WrongNameError(0, 0)
       
    
def validateResourceName(name):
    """
    Check if C{name} complies to L{RESOURCE_RE} and L{RESOURCE_FIRST_RE}.
    
    @param name: name of resource/collection
    @type name: unicode-string
    @raise WrongNameError: if validation fails (see L{datafinder.common.NameCheck.WrongNameError})
    """
    illegalChar = RESOURCE_RE.search(name)
    if illegalChar:
        raise WrongNameError(illegalChar.start(), name[illegalChar.start()])
    if not RESOURCE_FIRST_RE.match(name):
        if len(name) > 0:
            raise WrongNameError(0, name[0])
        else:
            raise WrongNameError(0, 0)

def getResourceNameErrorPosition(name):
    """
    Get position of illegal character (and the error-message).
    This method can be used to get this information if L{isValidPropertyName}
    or L{isValidResourceName} failed.
    
    @param name: name of resource/collection
    @type name: unicode-string
    
    @return: tuple of error-position and error-message
    @rtype: (int, unicode)-tuple
    """
    illegalChar = RESOURCE_RE.search(name)
    if illegalChar:
        result = (illegalChar.start(), \
                  u"Illegal character '%s' at index %d." % \
                      (name[illegalChar.start()], illegalChar.start()))
    elif not RESOURCE_FIRST_RE.match(name):
        result = (0, u"Illegal character '%s' at index %d." % (name[0], 0))
    else:
        result = (-1, None)
    return result

    
class WrongNameError(ValueError):
    """
    Exception raised if an "illegal" character was found.
    
    @ivar character: character that caused the exception
    @type character: C{unicode}
    @ivar position: position of C{character}
    @type position: C{int}
    """
    def __init__(self, position, character):
        ValueError.__init__(self)        
        self.character = character
        self.position = position
    
    def __str__(self):
        return ValueError.__str__(self) + \
            "Character '%s' at index %d." % (self.character, self.position)
