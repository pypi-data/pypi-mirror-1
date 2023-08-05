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

"""fellowiki wiki parser: support for escaped text

TODO
    
"""

from parser import Token, TextToken, ParagraphSeparatorToken, XMLElement

NO_WIKI_TAGS = 'no wiki tags'
PREFORMATTED = 'preformatted'
SINGLE_ESCAPED_CHARACTER = 'single escaped character'

class PreformattedTextToken(ParagraphSeparatorToken):
    def do_extended_close(self, inserted_token):
        embed = XMLElement('pre')
        embed.append(self.text)
        inserted_token.xhtml.append(embed)

def extend_wiki_parser(wiki_parser):
    wiki_parser.regexes[NO_WIKI_TAGS] = (10, r'\[%([^\\%\[]|\\.|%[^\\\]])*%\]', 
            TextToken, dict(cut_left = 2, cut_right = 2, decode_backslash = True))
    wiki_parser.regexes[PREFORMATTED] = (10, r'\[@([^\\@]|@?\\.|@[^\\\]])*@\]', 
            PreformattedTextToken, dict(preference = 0, cut_left = 2, cut_right = 2, 
                                    decode_backslash = True))
    wiki_parser.regexes[SINGLE_ESCAPED_CHARACTER] = (10, r'\\.', 
            TextToken, dict(cut_left = 1))
