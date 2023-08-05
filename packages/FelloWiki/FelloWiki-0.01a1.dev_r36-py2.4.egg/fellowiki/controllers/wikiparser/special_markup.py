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

from parser import Token, LineBreakToken, LINEBREAK, XMLElement, BetweenParagraphsXHTML

LINEBREAK_OUTPUT = 'linebreak output'
HORIZONTAL_RULE = 'horizontal rule'

class LineBreakOutputToken(LineBreakToken):
    def render(self, new_token):
        xhtml = XMLElement('br')
        new_token.prepend(xhtml)
        
    def evaluate(self, result, tokens, state, procs):
        while tokens[0].is_a(LINEBREAK):
            next_token = tokens.pop(0)
            self.token += next_token.token
        while len(result) >0 and result[-1].is_a(LINEBREAK):
            previous_result = result.pop()
            self.token = previous_result.token + self.token
        LineBreakToken.evaluate(self, result, tokens, state, procs)
        
    is_a = Token.is_a # a line break (output) is *not* a line break (input)
    
def extend_wiki_parser(wiki_parser):
    wiki_parser.regexes[LINEBREAK_OUTPUT] = (20, r'^%%%%%+[ \t]*(\n%%%%%+[ \t]*)*$',
                     LineBreakOutputToken, dict(preference = 1))
    wiki_parser.regexes[HORIZONTAL_RULE] = (10, r'^----$', BetweenParagraphsXHTML,
                     dict(xhtml = XMLElement('hr')))
