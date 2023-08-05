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

"""fellowiki wiki parser: lists

TODO
    
"""

from parser import ParagraphToken, XMLElement, PrefixToken

LIST_TAGS = {'*': ('ul', 'bullet'),
             '-': ('ul', 'dash'),
             '#': ('ol', 'ordered')}
LISTS = 'lists'
LIST_RESULT = 'list result'
                 
def _list_to_xhtml(list, is_sublist = False):
    xhtml = XMLElement('div')
    if is_sublist:
        container = None
    else:
        container = xhtml
    for (type, value) in list:
        if type == '':
            value.xhtml.tag = 'li'
            container = value.xhtml
            xhtml.append(value.xhtml)
        else:
            sublist = _list_to_xhtml(value, True)
            sublist.tag = LIST_TAGS[type][0]
            sublist.attributes['class'] = LIST_TAGS[type][1]
            if container is None:
                container = XMLElement('li')
                xhtml.append(container)
            container.append(sublist)
    return xhtml
    
class ListResultToken(ParagraphToken):
    # this is a paragraph, not a paragraph separator
    def __init__(self, lists, token):
        ParagraphToken.__init__(self, token)
        self._list = XMLElement()
        self.xhtml.append(self._list)
        self.lists = lists
    
    def do_extended_close(self, inserted_token):
        self._list.content = _list_to_xhtml(self.lists).content
        inserted_token.xhtml.append(*self.xhtml.content)
    
    def is_a(self, *capabilities):
        return LIST_RESULT in capabilities or ParagraphToken.is_a(self, *capabilities)
            

class ListToken(PrefixToken): 
    def __init__(self, token, *args, **kwargs):
        PrefixToken.__init__(self, token, *args, **kwargs)
        self.lists = []
    def do_prefix(self, new_token):
        assert(len(self.lists) == 0)
        if len(self.result) > 0 and self.result[-1].is_a(LIST_RESULT):
            self.lists = self.result.pop().lists
        current_list = self.lists
        for list_type in self.token[:-1]:
            if len(current_list) == 0 or current_list[-1][0] != list_type:
                new_list = []
                current_list.append((list_type, new_list))
                current_list = new_list
            else:
                current_list = current_list[-1][1]
        current_list.append(('', new_token))
        
        self.result.append(ListResultToken(self.lists,self.token))
        
    def render(self, new_token):
        PrefixToken.render(self, new_token)
        
def extend_wiki_parser(wiki_parser):
    wiki_parser.regexes[LISTS] = (10, r'^[#*-]+[ \t]', ListToken, dict(preference = 30))
