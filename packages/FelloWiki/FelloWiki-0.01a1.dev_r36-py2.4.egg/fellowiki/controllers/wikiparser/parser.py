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

"""fellowiki wiki parser

TODO: overview wiki parser
    
"""

from fellowiki.util.assorted import attributes_from_dict
import elementtree.ElementTree as ElementTree
from fellowiki.util.xmlelement import XMLElement
from util import remove_backslashes_and_whitespace, remove_escaping_backslashes
      
import sre
import re
from copy import deepcopy


PREFIX_COUNT = "prefix count"


PROC = 'procedure'

WHITESPACE = 'white space'
TEXT = 'text'
LINEBREAK = 'line break'
STRUCTUREMOD = 'structure modifier'
PARAGRAPH = 'paragraph'
END_TOKEN = 'end token'
ENCAPSULATE_TOKEN = 'encapsulate token'
PREFIX = 'prefix'

class WikiError(StandardError):
    pass

class WikiParserError(WikiError):
    pass

class WikiTokenError(WikiError):
    pass
    
class Token(object):
    def __init__(self, token, cut_right = None, cut_left = None,
                     decode_backslash = False, preference = None, **attr_dict):
        attributes_from_dict(dict(locals().items()+attr_dict.items()))
        try:
            cut_right = -cut_right
        except TypeError: 
            pass
        self.text = token[cut_left:cut_right]
            
        if decode_backslash:
            self.text = remove_escaping_backslashes(self.text)
            
    def render(self, new_token):
        new_token.prepend(self.token)
        
    def match_is_open(self):
        return False
    
    def close_matching(self, match):
        return False
    
    def evaluate(self, result, tokens, state, procs):
        self.result = result
        self.tokens = tokens
        self.state = state
        
        new_token = ResultToken()
        
        # fold result set where appropriate (e.g. higher priority) and
        # close matching "braces"
        while result \
            and (self.preference is not None 
                    and (result[-1].preference > self.preference 
                        or self.preference < 0
                        or len(result) > 1 and result[-1].preference is None 
                            and (result[-2].preference is None 
                                or result[-2].preference > self.preference)
                        or self.match_is_open()) 
                or self.preference is None 
                    and result[-1].preference is None):
            res = result.pop()
            if self.close_matching(res):
                # matching braces generate a new token that will be evaluated
                # as a new token
                self.close(res, new_token)
                return
            else:
                res.render(new_token)
                
        if new_token.xhtml.is_not_empty(): 
            result.append(new_token)
            
        if not self.is_a(END_TOKEN):
            result.append(self)
    
    def is_a(self, *capabilities):
        return False
            

class ResultToken(Token):
    def __init__(self):
        attributes_from_dict(locals())
        self.preference = None
        self.xhtml = XMLElement('div')
        
    def render(self, new_token):
        new_token.prepend_element_contents(self.xhtml)
    
    def prepend(self, *prependee):
        self.xhtml.prepend(*prependee)
        
    def append(self, *appendee):
        self.xhtml.append(*appendee)
    
    def prepend_element_contents(self, element):
        self.xhtml.prepend(*element.content)
        
    def append_element_contents(self, element): 
        self.xhtml.append(*element.content)

class EndToken(Token):
    def __init__(self):
        attributes_from_dict(locals())
        self.preference = -1
        
    def render(self, new_token):
        pass
        
    def match_is_open(self):
        return True
    
    def is_a(self, *capabilities):
        return END_TOKEN in capabilities

class TextToken(Token):
    def __init__(self, token, new_text = None, **attr_dict):
        Token.__init__(self, token, new_text = new_text, **attr_dict)
        
    def render(self, new_token):
        if self.new_text is None:
            text = re.sub('[ \n\t]+', ' ', self.text)
        else:
            text = re.sub('[ \n\t]+', ' ', self.new_text)
        new_token.prepend(text)

class WhitespaceToken(TextToken):
    def is_a(self, *capabilities):
        return WHITESPACE in capabilities

class PrefixToken(Token):
    def __init__(self, token, *args, **kwargs):
        self.has_been_prefixed = False
        Token.__init__(self, token, *args, **kwargs)
        
    def evaluate(self, result, tokens, state, procs):
        state[PREFIX_COUNT] = state.get(PREFIX_COUNT, 0) + 1
        Token.evaluate(self, result, tokens, state, procs)
        
    def render(self, new_token):
        self.state[PREFIX_COUNT] = self.state.get(PREFIX_COUNT, 0) - 1
        Token.render(self, new_token)
    
    def prefix(self, new_token):
        self.has_been_prefixed = True
        if new_token.xhtml.is_empty():
            self.tokens.insert(0, new_token)
            self.tokens.insert(0, self)
        else:
            self.do_prefix(new_token)    
            
    def is_a(self, *capabilities):
        return PREFIX in capabilities
          
class LineBreakToken(Token):
    def render(self, new_token):
        new_token.prepend(' ')
        
    def evaluate(self, result, tokens, state, procs):
        if self.is_a(LINEBREAK) and tokens[0].is_a(LINEBREAK):
            next_token = tokens.pop(0)
            tokens.insert(0, ParagraphToken(self.token + next_token.token))
        else:
            Token.evaluate(self, result, tokens, state, procs)
    
    def match_is_open(self):
        return self.state.get(PREFIX_COUNT, 0) > 0
    
    def close_matching(self, match):
        return match.is_a(PREFIX) and not match.has_been_prefixed
        
    def close(self, match, new_token):
        self.state[PREFIX_COUNT] = self.state.get(PREFIX_COUNT, 0) - 1
        if self.state[PREFIX_COUNT] > 0 or not self.is_a(LINEBREAK):
            self.tokens.insert(0, self)
        match.prefix(new_token)
        
    def is_a(self, *capabilities):
        return LINEBREAK in capabilities

           
class ParagraphToken(LineBreakToken):
    def __init__(self, token, *args, **kwargs):
        LineBreakToken.__init__(self, token, *args, **kwargs)
        self.preference = 0
        self.xhtml = XMLElement('div')
        self.modifiers = {}
        
    def match_is_open(self):
        return True
    
    def close_matching(self, match):
        return match.is_a(PARAGRAPH) \
            or LineBreakToken.close_matching(self, match) 
           
    def evaluate(self, result, tokens, state, procs): 
        while result and result[-1].is_a(LINEBREAK):
            previous_result = result.pop()
            self.token = previous_result.token + self.token
        
        caught_line_break = False
        
        while tokens[0].is_a(WHITESPACE, STRUCTUREMOD, LINEBREAK, PARAGRAPH):
            next_token = tokens.pop(0)
            if next_token.is_a(PARAGRAPH) or \
                caught_line_break and next_token.is_a(LINEBREAK):
                self.modifiers = {}
            caught_line_break = next_token.is_a(LINEBREAK)
            try:
                next_token.modify(self.modifiers)
            except AttributeError:
                pass
            
        LineBreakToken.evaluate(self, result, tokens, state, procs)
        
    def close(self, match, new_token):
        if LineBreakToken.close_matching(self, match):
            LineBreakToken.close(self, match, new_token)
        else:
            if new_token.xhtml.is_not_empty():
                new_token.xhtml.tag = 'p'
                
                for (key, value) in match.modifiers.items():
                    if key == 'align':
                        new_token.xhtml.attributes['class'] = 'align-%s' % value
                match.modifiers = self.modifiers   ### shouldn't we reconsider and insert self?
                
                match.xhtml.append(new_token.xhtml)
            self.tokens.insert(0, match)
            self.do_extended_close(match)
            
    def do_extended_close(self, inserted_token):
        pass
        
    def render(self, new_token):
        new_token.prepend_element_contents(self.xhtml)
            
    def is_a(self, *capabilities):
        return PARAGRAPH in capabilities
 
class ParagraphSeparatorToken(ParagraphToken):
    is_a = Token.is_a
 
class EncapsulateToken(Token):
    def __init__(self, token, *args, **kwargs):
        Token.__init__(self, token, *args, **kwargs)
        self.consumed_whitespace_left = False
        self.consumed_whitespace_right = False
        
    def render(self, new_token):
        if self.type == '(':
            self.state[self.STATE] = self.state.get(self.STATE, 0) - 1
        Token.render(self, new_token)
    
    def evaluate(self, result, tokens, state, procs):
        ## there can be only one WhitespaceToken in a row
        if self.type <> '(' and result and result[-1].is_a(WHITESPACE):
            result.pop()
            if not self.consumed_whitespace_left:
                self.consumed_whitespace_left = True
                self.token = ' ' +  self.token
        while self.type <> ')' and tokens and tokens[0].is_a(WHITESPACE):
            tokens.pop(0)
            if not self.consumed_whitespace_right:
                self.consumed_whitespace_right = True
                self.token = self.token + ' '
        
        Token.evaluate(self, result, tokens, state, procs)
        if self.type == '(':
            state[self.STATE] = state.get(self.STATE, 0) + 1
        
    def match_is_open(self):
        if self.type == ')':
            return self.state.get(self.STATE, 0) > 0
        return False
    
    def close_matching(self, match):
        return (self.state.get(self.STATE, 0) == 1 and
                self.type == ')' and match.is_a(ENCAPSULATE_TOKEN) and 
                self.STATE == match.STATE and self.text == match.text and 
                match.type in ('(', '_'))
            
    def close(self, match, new_token):
        if match.type == '(':
            self.state[self.STATE] = self.state.get(self.STATE, 0) - 1
        self.insert_result(match, new_token)    
            
    def insert_result(self, match, result_token):
        self.tokens.insert(0, result_token)
        
    def is_a(self, *capabilities):
        return ENCAPSULATE_TOKEN in capabilities
   

class BetweenParagraphsXHTML(ParagraphSeparatorToken):
    def __init__(self, token, xhtml):
        ParagraphToken.__init__(self, token)
        self.xhtml = xhtml
    
    def do_extended_close(self, inserted_token):
        inserted_token.xhtml.append(self.xhtml)
        
def _token_factory(token_cls, kw_args):
    def new_token(_, token):
        return token_cls(token, **kw_args)
    return new_token    
        
class WikiParser(object):
    regexes = {LINEBREAK: (40, r'[ \t]*\n[ \t]*', LineBreakToken, dict(preference = 20)),
               WHITESPACE: (90, r'[ \t]+', WhitespaceToken, dict()),
               TEXT: (99, r'.[a-zA-Z0-9]*', TextToken, dict())}

    def __init__(self, procs, extensions):
        self.regexes = deepcopy(self.regexes) # copy per instance
        for extension in extensions:
            extension.extend_wiki_parser(self)
        regexes = self.regexes.values()
        regexes.sort()
        regexes = [(rex, _token_factory(class_, kw_args)) for 
                                    (_, rex, class_, kw_args) in regexes]
        self.scanner = sre.Scanner(regexes, sre.M)
        self.procs = procs

    def parse(self, text):
        import time
        
        text = re.sub('\r\n', '\n', text)
        tokens = self.scanner.scan(''.join(['\n\n', text, '\n\n']))
        
        if tokens[1] != '':
            raise WikiParserError('WikiParser error in "%s"' % text)
        
        tokens = tokens[0]
        tokens.append(EndToken())
        result = []
        state = {}
        
        while tokens:
            token = tokens.pop(0)
            token.evaluate(result, tokens, state, self.procs)
        
        if bool(tokens):
            raise WikiParserError('WikiParser error in "%s"' % text)
        if len(result) > 1:
            raise WikiParserError('WikiParser error in "%s"' % text)
            
        if len(result) == 1:    
            xhtml_tree, translations = result[0].xhtml.to_element_tree()
            
        else:
            xhtml_tree = ElementTree.Element('div')
            translations = []
        
        xhtml_tree.set('class','parsed-wiki-content')
        
        return (xhtml_tree, translations)
        
    def evaluate(self, tree):
        tree_  = deepcopy(tree)
        for trans in tree_[1]:
            self.procs[trans[1]][PROC](trans[0], *trans[2])
        return tree_[0]
