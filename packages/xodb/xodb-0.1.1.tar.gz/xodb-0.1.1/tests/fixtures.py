from __future__ import absolute_import

import xodb
from xodb import Attribute
from xodb.backends.xapian import XapianSchema, XapianAttribute
import datetime

class Ding(object):
    
    def __init__(self, bar):
        self.bar = bar
        self.blig = 41
        self.bloog = 42

        self.language = 'en'
        self.name = 'ding'
        self.direction = 'north'
        self.title = 'The young and the database.'
        self.instructions = 'Under the walker'
        self.zig = 3
#        self.creation_date = datetime.datetime(1999, 12, 31)


class DingSchema(XapianSchema):

    bar  = Attribute(type=Bar)
    zig  = Attribute(required=False)
    blig = Attribute(volatile=True)

    name          = XapianAttribute(text=True)
    direction     = XapianAttribute(prefixed=True)
    title         = XapianAttribute(text=True, language='fr')
    instructions  = XapianAttribute(prefixed=True, text=True, language='es')
#    creation_date = Attribute(Value())


