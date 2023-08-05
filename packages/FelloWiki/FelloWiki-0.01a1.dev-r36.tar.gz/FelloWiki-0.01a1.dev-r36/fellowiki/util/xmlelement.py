# pylint: disable-msg=W0613,E0201
# W0702, W0706: allow argument magic (i.e. attributes_from_dict())

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

"""

TODO
    
"""

from copy import copy
import elementtree.ElementTree as ElementTree
        
class XMLElement(object):
    def __init__(self, tag = None, content=None, prepend_to=None,
                 append_to=None, **attributes):
        self.tag = tag
        if content is None:
            self.content = []
        else:
            try:
                content.pop # check if it's a kind of list
                self.content = content
            except AttributeError:
                self.content = [content]
        self.attributes = {}
        
        for (key, val) in attributes.items():
            if key[-1:] == '_':
                self.attributes[key[:-1]] = val
            else:
                self.attributes[key] = val
            
        self.callback = []
        self.translations = []
        
        if prepend_to is not None:
            prepend_to.prepend(self)
        if append_to is not None:
            append_to.append(self)
        
    def clone(self, other):
        self.tag = other.tag
        self.content = other.content
        self.attributes = other.attributes
        self.callback = other.callback
        self.translations = other.translations
        
    def to_element_tree(self): 
        xhtml = ElementTree.Element(self.tag)
        sub_xhtml = None
        current_textlist = []
        content = copy(self.content)
        translations = []
        
        for (key, val) in self.attributes.items():
            xhtml.set(key, str(val))
        
        # I want to modify the list, therefore I write this a bit 
        # more explicitly:
        while content:
            item = content.pop(0) 
            try: # should work, if it's a text list
                current_textlist.extend(item)
            except TypeError: # should be an XMLElement
                if item.tag is None:
                    content = item.content + content
                else:
                    current_text = ''.join(current_textlist)
                    current_textlist = []
                    if sub_xhtml is None:
                        xhtml.text = current_text
                    else:
                        sub_xhtml.tail = current_text
                    sub_xhtml, sub_translations = item.to_element_tree()
                    xhtml.append(sub_xhtml)
                    translations.extend(sub_translations)
        current_text = ''.join(current_textlist)
        if sub_xhtml is None:
            xhtml.text = current_text
        else:
            sub_xhtml.tail = current_text
        for translation in self.translations:
            if translation[1] is None:
                translations.append((xhtml, 
                                     translation[0], 
                                     translation[2]))
            else:
                translation[1](xhtml, translation[2])
        return xhtml, translations
        
    def is_empty(self):
        return not bool(self.content)
        
    def is_not_empty(self):
        return bool(self.content)
            
    def append(self, *appendee):
        self.content.extend(appendee)
    
    def prepend(self, *prependee):
        self.content = list(prependee) + self.content
        
    def set(self, key, val):
        self.attributes[key] = val
        
    def get(self, key):
        return self.attributes[key]
        
def SubElement(parent, *args, **kwargs):
    return XMLElement(append_to=parent, *args, **kwargs)
