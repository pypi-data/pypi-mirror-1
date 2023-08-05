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

import turbogears.database

md = turbogears.database.metadata

from datetime import datetime

DEFAULT_STRING_LENGTH = 200
DEFAULT_COMMENT_LENGTH = 2000


__all__ = ['db_version', 'visit', 'group', 'user', 'permission', 'user_group',
           'group_permission', 'visit_identity', 'wiki', 'wiki_item_type', 
           'wiki_item', 'wiki_registry']

db_version = Table('fw_db_version', md,
    Column('prj', Unicode(30), nullable = False, primary_key = True),
    Column('db_version', Integer, nullable = False, primary_key = True),
    Column('installation_date', DateTime, default = datetime.utcnow))

visit = Table('fw_visit', md,
    Column('visit_key', String(40), primary_key=True),
    Column('created', DateTime, nullable=False, default=datetime.utcnow),
    Column('expiry', DateTime))
        
group = Table('fw_group', md,
    Column('group_id', Integer, primary_key=True),
    Column('group_name', Unicode(16), unique=True),
    Column('display_name', Unicode(DEFAULT_STRING_LENGTH)),
    Column('created', DateTime, default=datetime.utcnow))
    
user = Table('fw_user', md,
    Column('user_id', Integer, primary_key=True),
    Column('user_name', Unicode(16), unique=True),
    Column('display_name', Unicode(DEFAULT_STRING_LENGTH)),
    Column('password', Unicode(40)),
    Column('created', DateTime, default=datetime.utcnow))

permission = Table('fw_permission', md,
    Column('permission_id', Integer, primary_key=True),
    Column('permission_name', Unicode(16), unique=True),
    Column('description', Unicode(DEFAULT_STRING_LENGTH)))

user_group = Table("fw_user_group", md, 
    Column("user_id", Integer, ForeignKey(user.c.user_id), primary_key=True),
    Column("group_id", Integer, ForeignKey(group.c.group_id), primary_key=True))

group_permission = Table("fw_group_permission", md,
    Column("group_id", Integer, ForeignKey(group.c.group_id), primary_key=True),
    Column("permission_id", Integer, ForeignKey(permission.c.permission_id), primary_key=True))

visit_identity = Table('fw_visit_identity', md,
    Column('visit_key', String, ForeignKey(visit.c.visit_key), primary_key=True), # foreign key *not* in quickstarted project
    Column('user_id', Integer, ForeignKey(user.c.user_id), index=True))
    
wiki = Table('fw_wiki', md,
    Column('wiki_id', Integer, Sequence('fw_wiki_seq'), primary_key = True, nullable = False),
    Column('name', Unicode(DEFAULT_STRING_LENGTH), nullable = False, unique = True),
    Column("read_permission_id", Integer, ForeignKey(permission.c.permission_id)),
    Column("protect_read_history", Boolean),
    Column("write_permission_id", Integer, ForeignKey(permission.c.permission_id)),
    Column("admin_permission_id", Integer, ForeignKey(permission.c.permission_id)))

#pre-load
wiki_item_type = Table('fw_wiki_item_type', md,
    Column('wiki_item_type_id', Integer, Sequence('fw_wiki_item_type_seq'), primary_key = True, nullable = False),
    Column('name', Unicode(DEFAULT_STRING_LENGTH), unique = True, nullable = False),
    Column('mime_type', String(DEFAULT_STRING_LENGTH), nullable = False),
    Column('binary', Boolean, nullable = False),
    Column('text', Boolean, nullable = False),
    Column('wiki_text', Boolean, nullable = False))

wiki_item = Table('fw_wiki_item', md,
    Column('wiki_item_id', Integer, Sequence('fw_wiki_item_seq'), primary_key = True, nullable = False),
    Column('name', Unicode(DEFAULT_STRING_LENGTH), unique = 'fw_i_wiki_item_unique', nullable = False),
    Column('version', Integer, unique = 'fw_i_wiki_item_unique', nullable = False),
    Column('wiki_id', Integer, ForeignKey(wiki.c.wiki_id), unique = 'fw_i_wiki_item_unique', nullable = False),
    Column('type_id', Integer, ForeignKey(wiki_item_type.c.wiki_item_type_id), nullable = False),
    Column('text_content', Unicode),
    Column('binary_content', Binary),
    Column('cache', PickleType),
    Column('created', DateTime, default = datetime.utcnow, nullable = False),
    Column('deleted', DateTime))

wiki_registry = Table('fw_wiki_registry', md,
    Column('wiki_registry_id', Integer, Sequence('fw_wiki_registry_seq'), primary_key = True, nullable = False),
    Column('wiki_id', Integer, ForeignKey(wiki.c.wiki_id), unique = 'fw_wiki_reg_unique'),
    Column('key', Unicode(DEFAULT_STRING_LENGTH), unique = 'fw_wiki_reg_unique'),
    Column('type', String(1)),
    Column('value_string', Unicode(DEFAULT_STRING_LENGTH)),
    Column('value_integer', Integer),
    Column('value_boolean', Boolean),
    Column('value_datetime', DateTime))
    
