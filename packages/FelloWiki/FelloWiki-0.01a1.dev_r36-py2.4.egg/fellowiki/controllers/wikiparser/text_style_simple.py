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

"""fellowiki wiki parser: special markup

TODO
    
"""

from parser import Token, XMLElement, WHITESPACE
from text_style import SPECIAL_MARKUP, EMBED_MARKUP, ENCAPSULATE_MARKUP

SWITCH_MARKUP = "switch markup"
  
class SwitchMarkupToken(Token):
    def __init__(self, token, *args, **kwargs):
        Token.__init__(self, token, *args, **kwargs)
        self.STATE = SWITCH_MARKUP + self.text
        self.EMBED = EMBED_MARKUP + self.text
    
    def evaluate(self, result, tokens, state, procs):
        Token.evaluate(self, result, tokens, state, procs)
        state[self.STATE] = state.get(self.STATE, 0) + 1

    def match_is_open(self):
        return self.state.get(self.STATE, 0) > 0

    def close_matching(self, match):
        return self.state.get(self.STATE, 0) == 1 \
            and match.is_a(SWITCH_MARKUP)
        
    def close(self, match, new_token):
        self.state[self.STATE] = self.state.get(self.STATE, 0) - 2
        if new_token.xhtml.is_not_empty():
            new_token.xhtml.tag = SPECIAL_MARKUP[self.text][0]
            new_token.xhtml.attributes['class'] = SPECIAL_MARKUP[self.text][1]
            if self.state.get(ENCAPSULATE_MARKUP + self.text, 0) > 0:
                if not self.state.has_key(self.EMBED):
                    self.state[self.EMBED] = []
                self.state[self.EMBED].append(new_token.xhtml)
            xhtml = XMLElement('div')
            xhtml.append(new_token.xhtml)
            new_token.xhtml = xhtml
        else:
            new_token.prepend(match.token)
            new_token.append(self.token)
            
        self.tokens.insert(0, new_token)

    def render(self, new_token):
        self.state[self.STATE] = self.state.get(self.STATE, 0) - 1
        Token.render(self, new_token)
        
    def is_a(self, *capabilities):
        return SWITCH_MARKUP in capabilities
        
def extend_wiki_parser(wiki_parser):
    regex_whitespace = wiki_parser.regexes[WHITESPACE]
    
    class WhitespaceToken(regex_whitespace[2]):
        def evaluate(self, result, tokens, state, procs):
            regex_whitespace[2].evaluate(self, result, tokens, state, procs)
            for key in SPECIAL_MARKUP.keys():
                state[SWITCH_MARKUP + key] = 0

    wiki_parser.regexes[WHITESPACE] = (regex_whitespace[0], regex_whitespace[1],
                            WhitespaceToken, regex_whitespace[3])
    wiki_parser.regexes[SWITCH_MARKUP] = (90, r'[/\*_=]', 
                            SwitchMarkupToken, dict(preference = 90))
