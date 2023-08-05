#!/usr/bin/python2.4
# Copyright (c) 2006 Jan Niklas Fingerle
#
# This source code file is based on a TurboGears "quickstarted" project.
# The TurboGears framework is copyrighted (c) 2005, 2006 by Kevin Dangoor 
# and contributors.
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


# If your project uses a database, you can set up database tests
# similar to what you see below. Be sure to set the db_uri to
# an appropriate uri for your testing database. sqlite is a good
# choice for testing, because you can use an in-memory database
# which is very fast.

from turbogears import testutil, database
# from fellowiki.model import YourDataClass, User

# database.set_db_uri("sqlite:///:memory:")

# class TestUser(testutil.DBTest):
#     def get_model(self):
#         return User
#
#     def test_creation(self):
#         "Object creation should set the name"
#         obj = User(user_name = "creosote",
#                       email_address = "spam@python.not",
#                       display_name = "Mr Creosote",
#                       password = "Wafer-thin Mint")
#         assert obj.display_name == "Mr Creosote"

