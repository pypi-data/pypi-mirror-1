#
# The Open Software License 3.0
#
# Copyright (c) 2008 Heikki Toivonen <My first name at heikkitoivonen.net>
#

from sqlalchemy import Table, Column, Unicode, Integer
from solu.utils import session, metadata

resource_table = Table('resources', metadata,
    Column('resource_id', Integer, primary_key=True),
    Column('name', Unicode(255), nullable=False),
    Column('email', Unicode(255)),
    Column('im', Unicode(255)),
    Column('x', Integer, nullable=False),
    Column('y', Integer, nullable=False)
)

class Resource(object):
    
    def __init__(self, name, email, im, x, y):
        self.name = name
        self.email = email
        self.im = im
        self.x = x
        self.y = y

    def __repr__(self):
        return '<Resource (%(rid)d: %(name)s <%(email)s> IM:%(im)s (%(x)d, %(y)d))>' % {
            'rid': self.resource_id,
            'name': self.name, 'email': self.email, 'im': self.im,
            'x': self.x, 'y': self.y}


session.mapper(Resource, resource_table)
