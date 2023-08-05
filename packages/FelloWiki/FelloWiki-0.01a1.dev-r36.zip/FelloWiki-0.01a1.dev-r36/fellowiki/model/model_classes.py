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

# TODO: add reference to quickstarted project


from sqlalchemy import *
from sqlalchemy.ext.assignmapper import assign_mapper

import turbogears.database

from fellowiki.util.assorted import attributes_from_dict
from schema import *

__all__ = ['DBVersion', 'Visit', 'VisitIdentity', 'Group', 'User',
           'Permission', 'Wiki', 'WikiItemType', 'WikiItem', 'Registry', 
           'initialize']

sc = turbogears.database.session.context

class DBVersion(object):
    def __init__(self, prj, db_version):
        self.prj = prj
        self.db_version = db_version
    def __repr__(self):
        return u"DBVersion(%s, %s)" %(repr(self.prj), repr(self.db_version))
        
assign_mapper(sc, DBVersion, db_version)


# visit and identity

class Visit(object):
    @classmethod
    def lookup_visit(cls, visit_key):
        return Visit.get(visit_key)
        
assign_mapper(sc, Visit, visit)


class VisitIdentity(object): pass
        
assign_mapper(sc, VisitIdentity, visit_identity)


class Group(object):
    def __init__(self, group_name, display_name, permissions):
        self.group_name = group_name
        self.display_name = display_name
        self.permissions.extend(permissions)
    
assign_mapper(sc, Group, group)

class User(object):
    def __init__(self, user_name, display_name, password, groups):
        self.user_name = user_name
        self.display_name = display_name
        self.password = password
        self.groups.extend(groups)
        
    def permissions(self):
        perms = set()
        for g in self.groups:
            perms = perms | set(g.permissions)
        return perms
    permissions = property(permissions)
        
assign_mapper(sc, User, user,
              properties = {'groups': relation(Group, secondary=user_group, backref='users')})
                  
                  
class Permission(object):
    def __init__(self, permission_name, description):
        attributes_from_dict(locals())
        
assign_mapper(sc, Permission, permission,
              properties = {'groups': relation(Group, secondary=group_permission, backref='permissions')})


# Wiki

class Wiki(object):
    def __init__(self, name, read_permission=None, 
                 write_permission=None, admin_permission=None,
                 protect_read_history=False):
        attributes_from_dict(locals())

assign_mapper(sc, Wiki, wiki,
              properties = {'read_permission': relation(Permission, primaryjoin=wiki.c.read_permission_id==permission.c.permission_id, backref='wiki_read_access'),
                            'write_permission': relation(Permission, primaryjoin=wiki.c.write_permission_id==permission.c.permission_id, backref='wiki_write_access'),
                            'admin_permission': relation(Permission, primaryjoin=wiki.c.admin_permission_id==permission.c.permission_id, backref='wiki_admin_access')})

class WikiItemType(object):
    def __init__(self, name, mime_type, binary=False, text=False, wiki_text=False):
        attributes_from_dict(locals())
    
assign_mapper(sc, WikiItemType, wiki_item_type)


class WikiItem(object):
    def __init__(self, name, version, wiki, item_type, text_content=None, binary_content=None, cache=None):
        self.name = name
        self.version = version
        if isinstance(wiki, Wiki):
            self.wiki = wiki
        else:
            self.wiki_id = wiki
        if isinstance(item_type, WikiItemType):
            self.item_type = item_type
        else:
            self.item_type = WikiItemType.selectone(WikiItemType.c.name == item_type)
        
        if text_content is not None:
            self.text_content = text_content 
        if binary_content is not None:
            self.binary_content = binary_content
        if cache is not None:
            self.cache = cache

assign_mapper(sc, WikiItem, wiki_item,
              properties = {'wiki': relation(Wiki),
                            'item_type': relation(WikiItemType)})
    
class Registry(object):
    TYPES = {'S': 'value_string',
             'I': 'value_integer',
             'B': 'value_boolean',
             'D': 'value_datetime'}
    
    def __init__(self, key, type, value):
        try:
            column_name = self.TYPES[type]
        except KeyError:
            raise NotImplementedError, 'Registry type "%s" not (yet) implemented' % type
            
        setattr(self, column_name, value)
        self.key = key
        self.type = type

assign_mapper(sc, Registry, wiki_registry,
              properties = {'wiki': relation(Wiki, backref='registry_items')})
                                
def initialize():
    from turbogears.database import metadata, get_engine
    metadata.create_all(engine=get_engine())
    
    DBVersion('FelloWiki - Base', 1)
    
    private_read = Permission('read private wiki', 'read access for the "private" wiki')
    private_write = Permission('write private wiki', 'write access for the "private" wiki')
    private_admin = Permission('admin private wiki', 'admin access for the "private" wiki')
    protected_write = Permission('write protected wiki', 'write access for the "protected" wiki')
    protected_admin = Permission('admin protected wiki', 'admin access for the "protected" wiki')
    public_admin = Permission('admin public wiki', 'admin access for the "public" wiki')
    
    user_group = Group('Users', 'Users', [public_admin, protected_admin, private_admin])
    admin_group = Group('Admins', 'Admins', [protected_write, private_write, private_read])
    
    admin_user = User('admin', 'Jane Admin', 'password', [user_group, admin_group])
    user_user = User('user', 'Joe User', 'password', [user_group])
    
    wiki_text = WikiItemType('wiki text', 'text/wiki', text = True, wiki_text = True)
    plain_text = WikiItemType('plain text', 'text/plain', text = True)
    css_text = WikiItemType('CSS', 'text/css', text = True)
    jpeg_image = WikiItemType('image: JPEG', 'image/jpeg', binary = True)
    gif_image = WikiItemType('image: GIF', 'image/gif', binary = True)
    bmp_image = WikiItemType('image: BMP', 'image/bmp', binary = True)
    png_image = WikiItemType('image: PNG', 'image/png', binary = True)
    
    wiki_private = Wiki('private', 
                        read_permission=private_read, 
                        write_permission=private_write,
                        admin_permission=private_admin)
    wiki_protected = Wiki('protected', 
                          write_permission=protected_write,
                          admin_permission=protected_admin)
    wiki_public = Wiki('public', 
                       admin_permission=public_admin)
                       
    for wiki in [wiki_private, wiki_protected, wiki_public]:
        wiki.registry_items.append(Registry('home page', 'S', 'Home Page'))
