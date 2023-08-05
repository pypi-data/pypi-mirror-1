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

import cherrypy
from turbogears import expose, controllers, validate, error_handler, identity

from turbogears.controllers import Controller, redirect
import turbogears
import turbogears.widgets as w
import turbogears.validators as v
import copy

from fellowiki.util.xmlelement import XMLElement, SubElement

from fellowiki.util.assorted import check_for_permission
from fellowiki.model import *

from fellowiki.widgets.forms import SubmitPreviewTableForm

from wikiparser.parser import WikiParser

from sqlalchemy import desc,asc, and_, or_
from sqlalchemy.exceptions import InvalidRequestError


from wikiparser import macros, tables, lists, headlines, special_characters, \
            escaped_text, links, special_markup, text_style, \
            text_style_simple, structure_modifiers

extensions = [macros, tables, lists, headlines, special_characters,
              escaped_text, links, special_markup, text_style,
              text_style_simple, structure_modifiers]

from fellowiki.model import *

__all__ = ['register_wikis']

        
def no_cache(f):
    def new_f(*args, **kwargs):
        cherrypy.response.headers['Pragma'] = 'no-cache'
        if cherrypy.response.version <> '1.0':
            cherrypy.response.headers['Cache-Control'] = 'no-cache'
        return f(*args, **kwargs)
    return new_f
        
def extract_ressource_key(num_args):
    def erp(f):
        def new_f(self, *args, **kw_args):
            return f(self, ressource_key=self.get_ressource_key(args[num_args:]),
                     *(args[0:num_args]), **kw_args)
        return new_f
    return erp
        
        
# Edit form
        
text_types = [(t.mime_type, t.name) 
                for t in WikiItemType.select(order_by=[desc(WikiItemType.c.wiki_text),
                                                            WikiItemType.c.name])
                if t.text]

binary_types = [(t.mime_type, t.name) 
                for t in WikiItemType.select(order_by=WikiItemType.c.name)
                if not t.text]

try:
    default_text_type = text_types[0][0]
except IndexError:
    default_text_type = None
        
try:
    default_binary_type = binary_types[0][0]
except IndexError:
    default_binary_type = None
        
wiki_edit_form = SubmitPreviewTableForm(
            fields=[w.TextArea(name='wiki_text', label='My Wiki Text', validator=v.NotEmpty),
                    w.TextField(name='comment', label='My Comment', validator=v.NotEmpty),
                    w.CheckBox(name='minor_change', label="This is a minor change."),
                    w.SingleSelectField(name="data type", label='My Data Type',  
                          options=text_types,   
                                    default=default_text_type
                          ),
                    w.HiddenField(name='version', validator=v.All(v.Int, v.NotEmpty))],
                    # validator = v.Schema(chained_validators=[v.FieldsMatch("comment",  "comment2")]),
                    submit_text="Save", preview_text="Preview", reset_text="Reset")
        
del text_types, binary_types, default_text_type, default_binary_type
        
        
class WikiInstance(Controller, identity.SecureResource):
    def __init__(self, wiki):
        self.name = wiki.name
        self.wiki_id = wiki.wiki_id
        self.parser = WikiParser([], extensions)
        self.registry = {}
        
        for entry in wiki.registry_items:
            try:
                column_name = Registry.TYPES[type]
                self.registry[entry.key] = getattr(entry, column_name)
            except KeyError:
                pass
        
        self.home_page = self.registry.get('home page', 'Home')

        if wiki.read_permission is not None:
            self.rd_perm = wiki.read_permission.permission_name
        else:
            self.rd_perm = None
            
        if wiki.write_permission is not None:
            self.wr_perm = wiki.write_permission.permission_name
        else:
            self.wr_perm = self.rd_perm
            
        if wiki.admin_permission is not None:
            self.adm_perm = wiki.admin_permission.permission_name
        else:
            self.adm_perm = self.wr_perm
            
        if wiki.protect_read_history:
            self.rd_hist_perm = self.wr_perm
        else:
            self.rd_hist_perm = self.rd_perm 
        
    def get_ressource_key(self, ressource_path = []):
        ressource_path = filter(None, ressource_path)
        if len(ressource_path) == 0:
            return self.home_page
        return '/'.join(ressource_path)
    
    @expose()
    @no_cache
    def index(self):
        check_for_permission(self.rd_perm)
        redirect("view/%s" % self.get_ressource_key())
        
        
        
    @expose(template="fellowiki.templates.wiki_view")
    @no_cache
    @extract_ressource_key(0)
    @validate(validators={"version": v.Int})
    def view(self, ressource_key, version=None, tg_errors={}):
        if version is None:
            check_for_permission(self.rd_perm)
        else:
            check_for_permission(self.rd_hist_perm)
        edit_link = '/'.join([cherrypy.request.object_path[:-5], 'edit', ressource_key])
        try:
            if version is None:
                current_version = WikiItem.selectone(and_(WikiItem.c.name==ressource_key,
                                                          WikiItem.c.wiki_id==self.wiki_id),
                                        order_by=desc(WikiItem.c.version),
                                        limit=1)    
            else:
                current_version = WikiItem.selectone(and_(WikiItem.c.name==ressource_key,
                                                          WikiItem.c.version==version,
                                                          WikiItem.c.wiki_id==self.wiki_id))
        except InvalidRequestError:
            if version is None:
                redirect(edit_link)
            else:
                raise cherrypy.NotFound
      
        parsed_content = self.parser.parse(current_version.text_content)
        content = self.parser.evaluate(parsed_content)
        
        page_is_editable = version is None
        
        
        
        return dict(title='FelloWiki - %s' % ressource_key, 
                    page_name=ressource_key, 
                    main_content=content,
                    edit_link=edit_link,
                    page_is_editable=page_is_editable)
            
            
    @expose()
    @extract_ressource_key(0)
    @validate(validators={"version": v.Int(not_empty=True)})
    def source(self, ressource_key, version=None, tg_errors={}):
        if version is None:
            check_for_permission(self.rd_perm)
        else:
            check_for_permission(self.rd_hist_perm)
        if len(tg_errors) > 0:
            raise cherrypy.NotFound
            
        try:
            selected_version = WikiItem.selectone(and_(WikiItem.c.name==ressource_key,
                                                       WikiItem.c.version==version,
                                                       WikiItem.c.wiki_id==self.wiki_id))
        except InvalidRequestError:
            raise cherrypy.NotFound
      
        item_type = selected_version.item_type
        cherrypy.response.headers['Content-Type'] = item_type.mime_type
        # TODO: set Header for encoding?
        
        if item_type.text:
            return selected_version.text_content
        else:
            return selected_version.binary_content
    
    # a bit hackish, but I want to have *all* of the decorators functionality
    # without decorating...
    @validate(form=wiki_edit_form)
    def validate_edit_form(self, tg_errors={}, **input_data):
        return tg_errors, input_data

    @expose(template="fellowiki.templates.wiki_edit") 
    @no_cache
    @extract_ressource_key(0)
    def edit(self, ressource_key, **input_data):
        check_for_permission(self.wr_perm)
        form_data = dict()
        preview = None
        
        try:
            prev_version = WikiItem.selectone(and_(WikiItem.c.name==ressource_key,
                                                   WikiItem.c.wiki_id==self.wiki_id),
                                       order_by=desc(WikiItem.c.version),
                                       limit=1)
        except InvalidRequestError:
            prev_version = None
      
         
        if len(input_data) == 0:
            if prev_version is None:
                form_data['version'] = 0
            else:
                form_data['wiki_text'] = prev_version.text_content
                form_data['version'] = prev_version.version
                
        else:
            parsed_content = self.parser.parse(input_data['wiki_text'])
            preview = self.parser.evaluate(parsed_content)
            
            tg_errors, input_data = self.validate_edit_form(**input_data)
            
            if len(tg_errors) == 0:
                
                item = WikiItem(ressource_key, input_data['version']+1, self.wiki_id,
                                'wiki text', text_content=input_data['wiki_text'], 
                                cache=parsed_content)
                redirect('/'.join([cherrypy.request.object_path[:-5], 'view', ressource_key]))
                
                
        
        return dict(form=wiki_edit_form, data=form_data, preview = preview)


def register_wikis(parent):
    for wiki in Wiki.select():
        if not hasattr(parent, wiki.name):
            setattr(parent, wiki.name, WikiInstance(wiki))
