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
from urllib import quote, unquote, splitattr, splituser
from urlparse import urlsplit, urlunsplit    

from parser import Token, XMLElement
from util import remove_backslashes_and_whitespace

link_allowed_targets = ['http', 'ftp', 'mailto']
image_link_allowed_targets = ['http', 'ftp']
user_domain_schemes = ['mailto']

LINK = 'link'
IMAGE_LINK = 'image link'

def check_and_normalize_url(url, allowed_schemes):
    scheme, location, path, query, fragment = urlsplit(url)
    
    if scheme not in allowed_schemes:
        return None, url
        
    if scheme in user_domain_schemes:
        location = path
        path = query = fragment = ''
    
    if location is not None:
        user, host = splituser(location)
        if host <> '': ## idna encoding encodes '' ==> '.' :-(
            host = host.encode('idna')
        
        if user is not None:
            user = ':'.join([quote(unquote(u.encode('utf-8'))) for u in user.split(':')])
            location = u'%s@%s' % (user, host)
        else:
            location = host
    
    if path is not None:
        path_ = [splitattr(segment) for segment in path.split('/')]
        path_ = [(quote(unquote(seg.encode('utf-8'))), 
                    [u'='.join([quote(unquote(p.encode('utf-8'))) for p in parm_.split('=')]) 
                    for parm_ in parm])    
                for (seg, parm) in path_]
        
        path = []
        
        for (segment, parms) in path_:
            if len(parms) > 0:
                segment_ = u';'.join([segment, u';'.join(parms)])
                path.append(segment_)
            else:
                path.append(segment)
                
        path = u'/'.join(path)
    
    if query is not None:
        query = u'&'.join([u'='.join([quote(unquote(q.encode('utf-8'))) for q in query_.split('=')]) 
                           for query_ in query.split('&')])
    
    if fragment is not None:
        fragment = quote(unquote(fragment.encode('utf-8')))
    
    if scheme in user_domain_schemes:
        path = location
        location = ''
        
    return scheme, urlunsplit((scheme, location, path, query, fragment))
            
class LinkToken(Token): 
    def render(self, new_token):
        new_token.prepend(self.xhtml)
        
    def evaluate(self, result, tokens, state, procs):
        Token.evaluate(self, result, tokens, state, procs)
        
        self.xhtml = XMLElement('a')
        
        match_obj = re.match(r'\[\[(([^\\\]]|\\.|\](?=[^\]]))*)' \
                               r'>>(([^\\\]]|\\.|\](?=[^\]]))*)\]\]', 
                             self.text)
        
        if match_obj:
            text, _, target, _ = match_obj.groups()
            text = remove_backslashes_and_whitespace(text)
            target = remove_backslashes_and_whitespace(target)
        else:
            text = target = remove_backslashes_and_whitespace(self.text[2:-2])
                
        self.xhtml.append(re.sub('[ \n\t]+', ' ', text))
        
        scheme, url = check_and_normalize_url(target, link_allowed_targets)
        
        if scheme is not None:
            if scheme == 'mailto':
                self.xhtml.attributes['class'] = 'link_mailto'
            else:
                self.xhtml.attributes['class'] = 'link_external'
            
            self.xhtml.attributes['href'] = url
            return
        
        try:
            link_proc = procs[LINK]
        except KeyError:
            self.xhtml.attributes['class'] = 'link_unresolved'
            self.xhtml.tag = 'span'
            return
            
        self.xhtml.translations.append((LINK, 
                                       None,
                                       [target]))
        self.xhtml.attributes['class'] = 'link_internal'
            
class ImageLinkToken(Token): 
    def render(self, new_token):
        new_token.prepend(self.xhtml)
        
    def evaluate(self, result, tokens, state, procs):
        Token.evaluate(self, result, tokens, state, procs)
        
        self.xhtml = XMLElement('a')
        
        # 1st attempt: description and link
        match_obj = re.match(r'\[\[\[(([^\\\]]|\\.|\]{1,2}(?=[^\]]))*)' \
                               r'\|\|(([^\\\]]|\\.|\]{1,2}(?=[^\]]))*)' \
                                 r'>>(([^\\\]]|\\.|\]{1,2}(?=[^\]]))*)\]\]\]',
                             self.text)
                             
        if match_obj:
            image, _, description, _, target, _ = match_obj.groups()
        else: # 2nd attempt: only link
            match_obj = re.match(r'\[\[\[(([^\\\]]|\\.|\]{1,2}(?=[^\]]))*)' \
                                     r'>>(([^\\\]]|\\.|\]{1,2}(?=[^\]]))*)\]\]\]', 
                                 self.text)
            if match_obj:
                image, _, target, _ = match_obj.groups()
                description = None
            else: # 3rd attempt: only description
                match_obj = re.match(r'\[\[\[(([^\\\]]|\\.|\]{1,2}(?=[^\]]))*)' \
                                       r'\|\|(([^\\\]]|\\.|\]{1,2}(?=[^\]]))*)\]\]\]', 
                                     self.text)
                if match_obj:
                    image, _, description, _ = match_obj.groups()
                    target = None
                else:
                    image = self.text[3:-3]
                    description = target = None
                    
        image = remove_backslashes_and_whitespace(image)
        if description is not None:
            description = remove_backslashes_and_whitespace(description)
            description = re.sub('[ \n\t]+', ' ', description)
        else:
            description = ''
            
        has_target = False
        
        if target is not None:
            has_target = True
            target = remove_backslashes_and_whitespace(target)
            scheme, url = check_and_normalize_url(target, link_allowed_targets)
            
            if scheme is not None:
                if scheme == 'mailto':
                    self.xhtml.attributes['class'] = 'link_mailto'
                else:
                    self.xhtml.attributes['class'] = 'link_external'
                self.xhtml.attributes['href'] = url
            else:    
                try:
                    link_proc = procs[LINK]
                    self.xhtml.translations.append((LINK, 
                                                    None,
                                                    [target]))
                    self.xhtml.attributes['class'] = 'link_internal'
                except KeyError:
                    self.xhtml.tag = 'span'
                    self.xhtml.attributes['class'] = 'link_unresolved'
                    
        scheme, url = check_and_normalize_url(image, image_link_allowed_targets)
        
        if scheme is not None:
            img = XMLElement('img')
            img.attributes['class'] = 'img_external'
            img.attributes['src'] = url
            
            img.attributes['alt'] = description
                
            if has_target:
                self.xhtml.append(img)
            else:
                self.xhtml = img
        else:   
            try:
                link_proc = procs[IMAGE_LINK]
                self.xhtml.translations.append((IMAGE_LINK, 
                                                None,
                                                [image, description, has_target]))
            except KeyError:
                span = XMLElement('span')
                
                span.append(re.sub('[ \n\t]+', ' ', image))
                if description <> '':
                    span.append(": %s" % description)
                    
                span.attributes['class'] = 'image_unresolved'
                self.xhtml.append(span)

          
def extend_wiki_parser(wiki_parser):
    wiki_parser.regexes[IMAGE_LINK] = (10, r'\[\[\[([^\\\]\n]|\\.|\]{1,2}(?=[^\]]))*\]\]\]', 
                    ImageLinkToken, dict(preference = 20))
    wiki_parser.regexes[LINK] = (20, r'\[\[([^\\\]\n]|\\.|\](?=[^\]]))*\]\]', 
                    LinkToken, dict(preference = 20))
