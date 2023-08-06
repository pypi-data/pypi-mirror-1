#
# The Open Software License 3.0
#
# Copyright (c) 2008 Heikki Toivonen <My first name at heikkitoivonen.net>
#

from os import path

from sqlalchemy import MetaData
from sqlalchemy.orm import create_session, scoped_session
from werkzeug import Local, LocalManager, Response, cached_property
from werkzeug.routing import Map, Rule
from mako.lookup import TemplateLookup

local = Local()
local_manager = LocalManager([local])
application = local('application')

metadata = MetaData()
session = scoped_session(lambda: create_session(application.database_engine,
                         transactional=True), local_manager.get_ident)

url_map = Map([Rule('/static/<file>', endpoint='static', build_only=True),
               Rule('/maps/<file>', endpoint='maps', build_only=True)])
def expose(rule, **kw):
    def decorate(f):
        kw['endpoint'] = f.__name__
        url_map.add(Rule(rule, **kw))
        return f
    return decorate

def url_for(endpoint, _external=False, **values):
    return local.url_adapter.build(endpoint, values, force_external=_external)

# calculate the path of the folder this file is in, the application will
# look for templates in that path
root_path = path.abspath(path.dirname(__file__))

# and calculate the static path as well
STATIC_PATH = path.join(root_path, 'static')

# create a mako template loader for that folder and set the default input
# encoding to utf-8
template_lookup = None
def install_template_lookup(module_directory=None):
    # XXX Is this safe?
    global template_lookup
    template_lookup = TemplateLookup(directories=[path.join(root_path, 'templates')],
                                     module_directory=module_directory,
                                     input_encoding='utf-8')

def render_template(template, **context):
    context['url_for'] = url_for
    return Response(template_lookup.get_template(template).render_unicode(**context),
                    mimetype='text/html')


class Pagination(object):

    def __init__(self, query, per_page, page, endpoint, **params):
        self.query = query
        self.per_page = per_page
        self.page = page
        self.endpoint = endpoint
        self.params = params

    @cached_property
    def count(self):
        return self.query.count()

    @cached_property
    def entries(self):
        return self.query.offset((self.page - 1) * self.per_page) \
                         .limit(self.per_page).all()

    has_previous = property(lambda x: x.page > 1)
    has_next = property(lambda x: x.page < x.pages)
    previous = property(lambda x: url_for(x.endpoint, page=x.page - 1, **x.params))
    next = property(lambda x: url_for(x.endpoint, page=x.page + 1, **x.params))
    pages = property(lambda x: max(0, x.count - 1) // x.per_page + 1)
