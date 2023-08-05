# Copyright (c) 2006 Jan Niklas Fingerle
# 
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.

"""fellowiki wiki parser: structure modifiers support

TODO
    
"""

from parser import Token, STRUCTUREMOD

STRUCTURE_MODIFIERS = {':': ('align',  'center'),
                       '(': ('align',  'left'),
                       ')': ('align',  'right'),
                       '^': ('valign', 'top'),
                       '-': ('valign', 'middle'),
                       ',': ('valign', 'bottom')}

class StructureModifyToken(Token): 
#modifiziert letzte geoeffnete struktur, wird dann wegfallen lassen => keine
# preference
    def modify(self, modifiers):
        (key, value) = STRUCTURE_MODIFIERS[self.text]
        modifiers[key] = modifiers.get(key, value)
        
    def is_a(self, *capabilities):
        if STRUCTUREMOD in capabilities:
            return True
        else:
            return Token.is_a(self, *capabilities)
          
def extend_wiki_parser(wiki_parser):
    wiki_parser.regexes[STRUCTUREMOD] = (10, r'<[:()^,\-]>', StructureModifyToken,
                    dict(cut_left = 1, cut_right = 1))
