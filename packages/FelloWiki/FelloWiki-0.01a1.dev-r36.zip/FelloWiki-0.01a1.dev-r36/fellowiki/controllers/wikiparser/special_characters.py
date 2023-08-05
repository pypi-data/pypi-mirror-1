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

"""fellowiki wiki parser: TODO support

TODO
    
"""

from parser import TextToken

NM_NO_DASH = 'n/m-dash: no dash'
M_DASH = 'm-dash'
N_DASH = 'n-dash'

def extend_wiki_parser(wiki_parser):
    wiki_parser.regexes[NM_NO_DASH] = (20, r'----+', TextToken, dict())
    wiki_parser.regexes[M_DASH] = (21, r'---', TextToken, dict(new_text = u'\u2014'))
    wiki_parser.regexes[N_DASH] = (22, r'--', TextToken, dict(new_text = u'\u2013'))
