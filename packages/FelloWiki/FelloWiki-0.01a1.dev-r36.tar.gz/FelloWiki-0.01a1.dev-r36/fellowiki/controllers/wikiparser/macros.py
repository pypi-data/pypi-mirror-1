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

"""fellowiki wiki parser: macro support

TODO
    
"""

import re

from parser import Token, XMLElement, BetweenParagraphsXHTML, PROC
from util import remove_backslashes_and_whitespace

SPLIT = 'split'
ESCAPE = 'escape'
DEFERRED = 'deferred'
BLOCK_LEVEL = 'block level'
MACRO = 'macro'


class MacroToken(Token): 
    def render(self, new_token):
        if not self.block_level:
            new_token.prepend(self.xhtml)
        
    def evaluate(self, result, tokens, state, procs):
        Token.evaluate(self, result, tokens, state, procs)
        
        self.proc = None
        self.proc_not_deferred = None
        self.parameter = []
        self.xhtml = XMLElement('span')
        self.xhtml.append(self.text)
        self.block_level = False
        
        match_obj = re.match(r'\{\{(([^\\\}\|]|\\.|\}(?=[^\}]))*)' \
                             r'\|(([^\\\}]|\\.|\}(?=[^\}]))*)\}\}', 
                             self.text)
                             
        
        if match_obj:
            command, _, parms, _ = match_obj.groups()
        else:
            command = self.text[2:-2]
            parms = None
             
        command = '%s%s' % (MACRO, remove_backslashes_and_whitespace(command))
        
        try:
            this_proc = procs[command]
        except KeyError:
            self.xhtml.attributes['class'] = 'macro_unresolved'
            return
        
        self.proc = command
        
        if parms is not None:
            if this_proc.get(SPLIT):
                if this_proc.get(ESCAPE):
                    self.parameter = [remove_backslashes_and_whitespace(par[0]) for 
                            par in re.findall(r'(([^\\,]|\\.)+)(?=|,)', parms)]
                else:
                    self.parameter = [par[0] for 
                            par in re.findall(r'(([^\\,]|\\.)+)(?=|,)', parms)]
            else:
                if this_proc.get(ESCAPE):
                    self.parameter = [remove_backslashes_and_whitespace(parms)]
                else:
                    self.parameter = [parms]
        if not this_proc.get(DEFERRED):
            self.proc_not_deferred = this_proc[PROC]
            
        self.xhtml.translations.append((self.proc, 
                                  self.proc_not_deferred,
                                  self.parameter))
        self.xhtml.attributes['class'] = 'macro_resolved'
        
        if this_proc.get(BLOCK_LEVEL):
            self.block_level = True
            self.xhtml.tag = 'p'
            self.tokens.insert(0, BetweenParagraphsXHTML(self.token, self.xhtml))
          
def extend_wiki_parser(wiki_parser):
    wiki_parser.regexes[MACRO] = (10, r'\{\{([^\\\}\n]|\\.|\}(?=[^\}]))*\}\}', 
                    MacroToken, dict(preference = 20))
