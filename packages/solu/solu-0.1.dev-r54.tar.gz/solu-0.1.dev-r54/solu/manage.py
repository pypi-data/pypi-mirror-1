#!/usr/bin/env python
#
# The Open Software License 3.0
#
# Copyright (c) 2008 Heikki Toivonen <My first name at heikkitoivonen.net>
#

from configobj import ConfigObj
from werkzeug import script

def make_app():
    from solu.application import Solu
    return Solu()

def make_shell():
    from solu import models, utils
    application = make_app()
    return locals()

def deploy(dburi='sqlite:///solu.db',
           inifile='./deploy.ini', datadir=''):
    """Deploy the application. This means creating the database and writing
    the deploy.ini file in the current directory with all needed settings to
    run the application."""
    config = ConfigObj(inifile)
    config['dburi'] = dburi
    if datadir:
        config['data'] = datadir
    config.write()
    
    make_app().init_database()

def generate_demo_data():
    from solu import utils
    from solu.models import Resource
    Resource(u'John Doe', u'john@example.com', u'', 100, 100)
    Resource(u'Jane Doe', u'jane@example.com', u'j_example_com', 200, 200)
    Resource(u'Printer 1.2.3.4', u'', u'', 300, 300)
    Resource(u'Grunt One', u'g1@example.com', u'', 100, 400)
    Resource(u'Grunt Two', u'g2@example.com', u'', 150, 400)
    Resource(u'Grunt Three', u'g3@example.com', u'', 200, 400)
    Resource(u'Grunt Four', u'g4@example.com', u'', 250, 400)
    Resource(u'Grunt Five', u'g5@example.com', u'', 300, 400)
    Resource(u'Grunt Six', u'g6@example.com', u'', 350, 400)
    Resource(u'Grunt Seven', u'g7@example.com', u'', 400, 400)
    Resource(u'Grunt Eight', u'g8@example.com', u'', 450, 400)
    Resource(u'Grunt Nine', u'g9@example.com', u'', 500, 400)
    Resource(u'Grunt Ten', u'g10@example.com', u'', 550, 400)
    Resource(u'Grunt Eleven', u'g11@example.com', u'', 600, 400)
    utils.session.commit()

def demodb():
    """Insert some resources into the db for demonstration purposes."""
    make_app()
    generate_demo_data()

def cleardb():
    """Clear the database, for example after trying the demo."""
    # XXX How could I just delete everything in the database?
    from solu import utils
    from solu.models import resource_table
    make_app()
    delete = resource_table.delete()
    utils.session.execute(delete)
    utils.session.commit()

def run_app():
    action_runserver = script.make_runserver(make_app, use_reloader=True)
    action_shell = script.make_shell(make_shell)
    action_deploy = deploy 
    action_demodb = demodb 
    action_cleardb = cleardb 
        
    script.run()

if __name__ == '__main__':
    run_app()
