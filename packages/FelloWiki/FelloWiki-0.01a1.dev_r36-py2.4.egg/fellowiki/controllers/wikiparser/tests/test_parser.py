# pylint: disable-msg=W0702,W0706
# W0702, W0706: allow exception handling scheme in new_test_func

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

# XHTML validating inspired by Cookbook, recipe 12.8 TODO: elaborate

"""unit tests for the classmates wiki parser

wer're using nosetests
"""

import codecs
import sys

from os.path import dirname, isdir, splitext, join, abspath, basename
from os import listdir
from copy import copy
from urllib import quote
from elementtree.ElementTree import tostring, fromstring, Element, SubElement
from xml.parsers.xmlproc import xmlval, utils, xmldtd

from fellowiki.controllers.wikiparser.parser import WikiParser, PROC
from fellowiki.controllers.wikiparser.links import LINK, IMAGE_LINK
from fellowiki.controllers.wikiparser.macros import SPLIT, ESCAPE, MACRO, \
                                  DEFERRED, BLOCK_LEVEL

from fellowiki.controllers.wikiparser import macros, tables, lists, headlines, special_characters, \
            escaped_text, links, special_markup, text_style, \
            text_style_simple, structure_modifiers

extensions = [macros, tables, lists, headlines, special_characters,
              escaped_text, links, special_markup, text_style,
              text_style_simple, structure_modifiers]

# Pre-load the xhtml DTD once, since reloading for each xmlproc
# would be a major performance hit.
_xhtml_dtd = xmldtd.load_dtd(join(dirname(abspath(__file__)), '..', '..', '..',
                                  'third_party', 'w3c', 'xhtml1-strict.dtd'))

def _assert_etrees(etree_1, etree_2):
    """assert that two ElementTrees are equal
    
    parameters: etree_1, 
                etree2:  two ElementTrees
    
    """
    
    assert etree_1.tag == etree_2.tag
    assert etree_1.text == etree_2.text
    assert etree_1.tail == etree_2.tail
    assert etree_1.attrib == etree_2.attrib
    
    children_1 = etree_1.getchildren()
    children_2 = etree_2.getchildren()
    
    assert len(children_1) == len(children_2)
    for (child_1, child_2) in zip(children_1, children_2):
        _assert_etrees(child_1, child_2)    

def wiki_ut(fname, tc_extension, parser1, parser2):
    """test translation of one wiki markup string
    
    parameters: fname: file name, see below
                tc_extension: test case extension name, see below
    returns: nothing
    throws: whatever exceptions occur during parsing of the wiki text
            and exceptions used by the unittest framework to signal 
            test failure
    
    The function parses the file <fname>.wiki and compares the result to 
    the content of <fname>.<tc_extension>.xml. 
    
    If the unit test fails (but not in case of errors), an attempt is 
    made, to write <fname>.<tc_extension>.generated.xml. If this write 
    attempt fails, it does so silently. 
    In any case the original fail or error (that occured before the 
    writing attempt) will be raised to the caller (i.e. the unit test 
    "test runner").
    
    """
    
    
    # unfortunately I need a new validator each time around (Bug in 
    # xmlval: part of the old file remains in the buffer)
    xhtml_validator = xmlval.XMLValidator()
    xhtml_validator.set_error_handler(utils.ErrorRaiser(xhtml_validator))
    xhtml_validator.val.dtd = xhtml_validator.dtd = \
                                   xhtml_validator.ent = _xhtml_dtd
    try:
        # parse wiki text to XML tree
        wiki_file = codecs.open('%s.wiki' % fname, 'r', 'utf8')
        wiki_text = wiki_file.read()
        wiki_file.close()
        parsed_content = parser1.parse(wiki_text)
        xhtml_tree_wiki = parser2.evaluate(parsed_content)
        
        # 'extend' tree to a complete XML tree
        xhtml_tree_wiki_ext = Element('html', 
                                      xmlns='http://www.w3.org/1999/xhtml')
        head = SubElement(xhtml_tree_wiki_ext,'head')
        SubElement(head,'title')
        body = SubElement(xhtml_tree_wiki_ext,'body')
        body.append(xhtml_tree_wiki)
        
        # do one 'round trip' to get a canonical form
        xhtml_text_wiki_ext = tostring(xhtml_tree_wiki_ext)
        xhtml_tree_wiki_ext_canonical = fromstring(xhtml_text_wiki_ext)
        
        # read expected XML tree from file
        try:
            xhtml_fn = '%s.%s.xml' % (fname, tc_extension)
            xhtml_file = codecs.open(xhtml_fn, 'r', 'utf8')
            xhtml_text = xhtml_file.read()
            xhtml_file.close()
        except IOError:
            raise AssertionError('could not open file %s' % xhtml_fn)
        xhtml_tree = fromstring(xhtml_text)
        
        # and now for the tests
        _assert_etrees(xhtml_tree, xhtml_tree_wiki_ext_canonical)
        xhtml_validator.parse_resource(xhtml_fn) # validate as XHTML
        
    except AssertionError, ex_val:
        # I want to re-raise *this* exception with full traceback, even if I
        # get another one inbetween
        ex_tb = sys.exc_info()[-1]
        try:
            gen_file = codecs.open('%s.%s.generated.xml' % 
                         (fname, tc_extension), 'w+','utf8')
            gen_file.write(xhtml_text_wiki_ext)
            gen_file.close()
        except:
            pass # it's only debug output after all
        raise AssertionError, ex_val, ex_tb 


def make_ut_wiki(tc_extension, parser1, parser2, tc_path = 
                 join(dirname(abspath(__file__)),'tests'),
                 **kwargs):
    """generate wiki test cases
    
    parameters: tc_extension: extension for XML file names ("<fname>.wiki" will
                              be compared to <fname>.<tc_extension>.xml)
                tc_path:      directory, where to look for *.wiki and *.xml 
                              files. Defaults to subdirectory "tests" of the 
                              directory where this file is located.
                **kwargs:     Any additional keyword arguments are passed to 
                              the wiki parser's __init__() method.
    returns: an instance of unittest.TestSuite
    throws: nothing to be expected
     
    Test cases and test suites are generated "the normal way" from classes. 
    Therefore the test case classes must be generated dynamically. In the end
    the internal structure of the test suites is more like normal test cases
    than if we had built the suites ourselves.
       
    """
        
    # find test files and subdirectories
    fnames = listdir(tc_path)
    fnames = [file_ for file_ in fnames if file_[0:1] != '.'] # no hidden files
    fnames = [join(tc_path, file_) for file_ in fnames] 
    files = [splitext(file_)[0] for file_ in fnames 
                                               if splitext(file_)[1] == '.wiki']
    dirs = [file_ for file_ in fnames if isdir(file_)]
    
    # for every *.wiki file generate a test method
    for file_ in files:
        yield wiki_ut, file_, tc_extension, parser1, parser2
    
    for dir_ in dirs:
        for tc in make_ut_wiki(tc_extension, parser1, parser2, tc_path = dir_):
            yield tc
    
def test_parser_typical():
    def _macro_test_proc(macro_name):
        def new_test_proc(element, *args):
            element.text = None
            xhtml = SubElement(element, 'span', {'class': 'test_macro_class'}) 
            xhtml.text = '{MACRO %s: %s}' % (macro_name, unicode(args))
        return new_test_proc
        
    def _link_test_proc(element, target):
        if target in ['link1', 'link 2', 'link   3', u'\xc4rger']:
            element.set('class', '%s_resolved' % element.get('class'))
            element.set('href', '/view/%s' % quote(target.encode('utf-8')))
        else:
            element.set('class', '%s_unresolved' % element.get('class'))
            element.set('href', '/edit/%s' % quote(target.encode('utf-8')))
    
    def _image_link_test_proc(element, image, description, new_subelement):
        if image in ['link1', 'link 2', 'link   3', u'\xe4\xf6\xfc', u'look out for \xe9\xe8\xea']:
            if new_subelement:
                xhtml = SubElement(element, 'img')
            else:
                xhtml = element
                xhtml.tag = 'img'
            
            xhtml.set('class', 'image_internal_resolved')
            xhtml.set('src', '/view_img/%s' % quote(image.encode('utf-8')))
            xhtml.set('alt', description)
            
        else:
            if new_subelement:
                xhtml = SubElement(element, 'span')
            else:
                xhtml = element
                xhtml.tag = 'span'
            xhtml.set('class', 'image_internal_unresolved')
            if description == '':
                xhtml.text = image
            else:
                xhtml.text = "%s: %s" % (image, description)
    
    procs = {MACRO + 'macro default': {PROC: _macro_test_proc('default macro'),
                                       SPLIT: True,
                                       ESCAPE: True},
             MACRO + 'macro no split': {PROC: _macro_test_proc('no split'),
                                          ESCAPE: True},
             MACRO + 'macro no escape': {PROC: _macro_test_proc('no escape'),
                                           SPLIT: True},
             MACRO + 'macro w/o s/e': {PROC: _macro_test_proc('no split, escape')},
             MACRO + 'macro deferred': {PROC: _macro_test_proc('deferred'),
                                        SPLIT: True,
                                        ESCAPE: True,
                                        DEFERRED: True},
             MACRO + 'macro block level': {PROC: _macro_test_proc('block level'),
                                           SPLIT: True,
                                           ESCAPE: True,
                                           BLOCK_LEVEL: True},
             MACRO + 'macro b/l, def': {PROC: _macro_test_proc('block level, deferred'),
                                        SPLIT: True,
                                        ESCAPE: True,
                                        DEFERRED: True,
                                        BLOCK_LEVEL: True},
             LINK: {PROC: _link_test_proc},
             IMAGE_LINK: {PROC: _image_link_test_proc}}
    
    for (num, name) in enumerate(['testmacro', 'test macro2', 'Test: -Macro3-',
                                  'testmacro4', 'testmacro5', 'testmacro6',
                                  'testmacro7', 'testmacro8', 'testmacro9',
                                  'test macro 10', 'test macro | 11 ',
                                  'test macro \\', 'test macro \\ ',
                                  'test macro \\\\', 'test macro \\\\ ']):
        procs[MACRO + name] = {PROC: _macro_test_proc('testmacro %i' % num),
                               SPLIT: True,
                               ESCAPE: True}
    
    
    procs2 = copy(procs)
    
    procs2[MACRO + 'macro default'] = {PROC: _macro_test_proc('default macro DEFERRED'),
                                       SPLIT: True,
                                       ESCAPE: True},
    
    procs2[MACRO + 'macro deferred'] = {PROC: _macro_test_proc('DEFERRED'),
                                        SPLIT: True,
                                        ESCAPE: True,
                                        DEFERRED: True}
                                    
    procs2[MACRO + 'macro b/l, def'] = {PROC: _macro_test_proc('DEFERRED and block level'),
                                        SPLIT: True,
                                        ESCAPE: True,
                                        DEFERRED: True,
                                        BLOCK_LEVEL: True}
    
    #set up wiki parser
    parser1 = WikiParser(procs = procs, extensions = extensions)
    parser2 = WikiParser(procs = procs2, extensions = extensions)

    for tc in make_ut_wiki('complete', parser1, parser2):
        yield tc
        
    parser1 = WikiParser(procs = procs, extensions = [])
    parser2 = WikiParser(procs = procs2, extensions = [])

    for tc in make_ut_wiki('no_extension', parser1, parser2):
        yield tc

    for extension in extensions:
        parser1 = WikiParser(procs = procs, extensions = [extension])
        parser2 = WikiParser(procs = procs2, extensions = [extension])
    
        for tc in make_ut_wiki('extension_%s' % extension.__name__.split('.')[-1], parser1, parser2):
            yield tc

def test_parser_without_test_procs():
    #set up wiki parser
                              
    parser = WikiParser(procs = {}, extensions = extensions)

    for tc in make_ut_wiki('no_test_procs', parser, parser):
        yield tc
