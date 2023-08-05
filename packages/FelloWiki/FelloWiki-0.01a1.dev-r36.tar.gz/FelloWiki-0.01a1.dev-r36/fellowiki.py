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

import pkg_resources
pkg_resources.require("TurboGears")

from optparse import OptionParser
from os.path import join, exists, dirname

import cherrypy
import turbogears
from turbogears.database import session
from sqlalchemy.exceptions import SQLError

from fellowiki.model import DBVersion, initialize

def get_configuration():
    parser = OptionParser()
    parser.add_option("-c", "--config", dest="config_file", type='string',
                  help="read configuration from FILE", metavar="FILE")
    parser.add_option("-u", "--database ", dest="db_uri", type='string',
                  help="data base URI", metavar="URI")
    parser.add_option("-b", "--bind", dest="server_host", type='string',
                  help="bind server to HOST", metavar="HOST")
    parser.add_option("-p", "--port", dest="server_port", type='int',
                  help="bind server to PORT", metavar="PORT")
    parser.add_option("--generate-tables", dest="generate_tables", 
                  action='store_true', default=False,
                  help="generate fellowiki data base tables")
    parser.add_option("--update-tables", dest="update_tables", 
                  action='store_true', default=False,
                  help="update fellowiki data base tables - not yet supported")
                  
    (options, args) = parser.parse_args()
    
    if len(args) <> 0:
        parser.error("positional parameters supplied, but not expected")
                      
    return options


def check_database(options):
    cherrypy.log('DB URI is %s' % cherrypy.config.get('sqlalchemy.dburi'), 'DB', 0)
    if cherrypy.config.get('sqlalchemy.dburi') in ['sqlite://', 'sqlite://:memory:', 
                                         'sqlite:///', 'sqlite:///:memory:']:
        # SQLite data bases require one DBApi per Thread. Cherrypy is 
        # multithreaded. Each thread will get its own *empty* memory DB, which
        # is not what we want, therefore...
        cherrypy.log("FelloWiki does not support SQLite memory data bases.", 'DB', 2)
        return False
    
    try: 
        versions = DBVersion.select()
        if options.generate_tables:
            cherrypy.log('generation of data base tables requested, but '+
                         'schema version table exists', 'DB', 1)
            return True
    except SQLError:
        if options.generate_tables:
            cherrypy.log('generating data base tables, as requested', 'DB', 0)
            initialize()
            session.flush()
            
        else:
            cherrypy.log("The FelloWiki data base tables seem not to be " 
                         + "installed. Please run FelloWiki with the flag " 
                         + "'--generate-tables' to create all needed tables.", 'DB', 2)
            return False
        
    return True

def config_turbogears(options):
    if options.config_file is not None:
        turbogears.config.update_config(configfile=options.config_file, 
            modulename="fellowiki.config")
    elif exists(join(dirname(__file__), "setup.py")):
        turbogears.config.update_config(configfile=join(dirname(__file__), "dev.cfg"),
            modulename="fellowiki.config")
    elif exists("/etc/fellowiki.cfg"):
        turbogears.config.update_config(configfile="/etc/fellowiki.cfg",
            modulename="fellowiki.config")

    new_conf = {}
    
    if options.server_host is not None:
        new_conf['server.socket_host'] = options.server_host
    if options.server_port is not None:
        new_conf['server.socket_port'] = options.server_port
    if options.db_uri is not None:   
        new_conf['sqlalchemy.dburi'] = options.db_uri
        
    turbogears.config.update({'global': new_conf})


def start_web_server():
    options = get_configuration()
    config_turbogears(options)
    if check_database(options):
        from fellowiki.controllers import FelloWikiRoot
        turbogears.start_server(FelloWikiRoot())
      
if __name__ == '__main__':
    start_web_server()
