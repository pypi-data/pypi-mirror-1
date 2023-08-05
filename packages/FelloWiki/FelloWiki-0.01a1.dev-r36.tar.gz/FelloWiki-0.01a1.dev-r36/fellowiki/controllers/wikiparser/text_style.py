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

"""fellowiki wiki parser: text style

TODO

TODO: translate Textauszeichnungen
    
"""

from parser import XMLElement, EncapsulateToken

EMBED_MARKUP = "embed markup"
ENCAPSULATE_MARKUP = "encapsulate markup"

STYLE_OPEN = 'style open'
STYLE_CLOSE = 'style close'

SPECIAL_MARKUP = {'/': ('em', 'italic'),
                  '*': ('b' , 'bold'),
                  '_': ('span', 'underlined'),
                  '=': ('tt', 'typewriter'), 
                  "'": ('span', 'single_quotes'),
                  '"': ('span', 'double_quotes'),
                  '^': ('span', 'superscript'),
                  ',': ('span', 'subscript'),
                  '#': ('span', 'large'),
                  '~': ('span', 'small')}

class EncapsulateMarkupToken(EncapsulateToken):
    def __init__(self, token, *args, **kwargs):
        EncapsulateToken.__init__(self, token, *args, **kwargs)
        self.STATE = ENCAPSULATE_MARKUP + self.text
        self.EMBED = EMBED_MARKUP + self.text

    def close(self, match, new_token):
        EncapsulateToken.close(self, match, new_token)
        if new_token.xhtml.is_not_empty():
            new_token.xhtml.tag = SPECIAL_MARKUP[self.text][0]
            new_token.xhtml.attributes['class'] = SPECIAL_MARKUP[self.text][1]
            xhtml = XMLElement('div')
            xhtml.append(new_token.xhtml)
            new_token.xhtml = xhtml
            for xhtml_purge in self.state.pop(self.EMBED,()):
                xhtml_purge.tag = None
        else:
            new_token.prepend(match.token)
            new_token.append(self.token)
        
def extend_wiki_parser(wiki_parser):
    wiki_parser.regexes[STYLE_OPEN] = (10, r'\[[/\*_=\'"^,#~]', EncapsulateMarkupToken, 
                    dict(type = '(', preference = 20, cut_left = 1))
    wiki_parser.regexes[STYLE_CLOSE] = (10, r'[/\*_=\'"^,#~]\]', EncapsulateMarkupToken, 
                    dict(type = ')', preference = 20, cut_right = 1))

              
              
