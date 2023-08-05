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

import re

def remove_escaping_backslashes(string):
    """translate string with escaping backslashes to un-escaped version
    
    parameters: string: escaped string, may be unicode as well
    returns: unescaped version of the string
    
    This function looks for any occurence of "\." where "." can be any
    single character and replaces it by the character "." itself.
    
    """
    
    pattern = re.compile(r'\\(.)') # TODO: don't recompile everytime around
    return pattern.sub(r'\1', string)
    
    
def remove_backslashes_and_whitespace(string):
    """remove escaping backslashes and enclosing whitespace
    
    parameters: string: escaped string, may be unicode as well
    returns: unescaped version of the string
    
    This function looks for any occurence of "\." where "." can be any
    single character and replaces it by the character "." itself.
    
    Additionally it removes all enclosing whitespace (i.e. blank and
    tab) which hadn't been escaped before.
    
    """
    
    string = string.lstrip(' \t')
    
    pattern = re.compile(r'(\\)(?=[ \t]*$)') # TODO: don't recompile everytime around
    string2 = pattern.sub(r'\\\\', string)
    
    if len(string) == len(string2):
        return remove_escaping_backslashes(string).rstrip(' \t')
    
    string = remove_escaping_backslashes(string)
    string2 = remove_escaping_backslashes(string2)
    
    if len(string) == len(string2):
        return string.rstrip(' \t')
    else:
        pattern = re.compile(r'([ \t])[ \t]*$') # TODO: don't recompile everytime around
        return pattern.sub(r'\1', string)
