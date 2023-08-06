#
# The Open Software License 3.0
#
# Copyright (c) 2008 Heikki Toivonen <My first name at heikkitoivonen.net>
#

import os

from configobj import ConfigObj
from sqlalchemy import create_engine
from werkzeug import Request, ClosingIterator, SharedDataMiddleware
from werkzeug.exceptions import HTTPException

from solu.utils import (session, metadata, local, local_manager, url_map,
                        install_template_lookup, STATIC_PATH)
from solu import views
import solu.models


class Solu(object):

    def __init__(self, inifile='./deploy.ini'):
        local.application = self
        config = ConfigObj(inifile)
        self.database_engine = create_engine(config['dburi'],
                                             convert_unicode=True)
        datadir = config.get('data', None)
        if datadir is not None:
            datadir = os.path.join(os.path.abspath(datadir), 'maps')
            install_template_lookup(os.path.join(datadir, 'templates'))
        else:
            datadir = STATIC_PATH
            install_template_lookup()
        self.dispatch = SharedDataMiddleware(self.dispatch,
                                             {
                                              '/static':  STATIC_PATH,
                                              '/favicon.ico': os.path.join(STATIC_PATH, 'favicon.ico'),
                                              '/maps': datadir
                                             })


    def init_database(self):
        metadata.create_all(self.database_engine)

    def dispatch(self, environ, start_response):
        local.application = self
        request = Request(environ)
        
        # Get rid of the script name that would appear in FastCGI installations
        # Modified from the Pylons sample
        env = {}
        for k,v in request.environ.items():
            env[k]=v
        env['SCRIPT_NAME'] = ''

        local.url_adapter = adapter = url_map.bind_to_environ(env)
        try:
            endpoint, values = adapter.match()
            handler = getattr(views, endpoint)
            response = handler(request, **values)
        except HTTPException, e:
            response = e
        return ClosingIterator(response(environ, start_response),
                               [session.remove, local_manager.cleanup])

    def __call__(self, environ, start_response):
        return self.dispatch(environ, start_response)
