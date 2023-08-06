import os.path

from zope.interface import Interface
from zope import schema

class Basics(Interface):
    
    first_name = schema.TextLine(title=u"First name")
    surname = schema.TextLine(title=u"Surname")
    employee_number = schema.ASCII(title=u"Employee number")
    
class Location(Interface):
    
    address = schema.Text(title=u"Full address")

class Interests(Interface):
    
    number_of_pets = schema.Int(title=u"Pets", min=0, default=3)
    birthday = schema.Date(title=u"Birthday")
    randomly_readonly = schema.Dict(title=u"Readonly dict", 
                                    key_type=schema.Int(title=u"Key"),
                                    value_type=schema.Int(title=u"Value"),
                                    default={1:1, 2:2},
                                    readonly=True)

class Override(Interface):
    
    birthday = schema.Datetime(title=u"Exact birth time", readonly=True)

zptlogo = open(os.path.join(os.path.dirname(__file__), 'zptlogo.gif'), 'rb').read()