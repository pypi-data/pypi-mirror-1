
from elixir import *

class Person(Entity):
        
    name = Field(Unicode(250), required=True)
    addresses = OneToMany('Address')
    phones = OneToMany('Phone')
    email = OneToMany('Email')
    email2 = OneToMany('Email2', cascade='delete, delete-orphan')
    email3 = OneToMany('Email3', passive_deletes=True)
    email3 = OneToMany('Email4', passive_deletes=True)
    
    using_options(tablename="person")
    
class Address(Entity):
    
    street = Field(Unicode(1000), required=True)
    person = ManyToOne('Person', required=True)
    
    using_options(tablename="addresses")
    
class Phone(Entity):
    
    number = Field(Unicode(15), required=True)
    person = ManyToOne('Person', ondelete='cascade')
    
    using_options(tablename="phones")

class Email(Entity):
    
    email = Field(Unicode(254), required=True)
    person = ManyToOne('Person', required=True, ondelete='cascade')
    
    using_options(tablename="emails")

class Email2(Entity):
    
    email = Field(Unicode(254), required=True)
    person = ManyToOne('Person', required=True, ondelete='cascade')
    
    using_options(tablename="emails2")

class Email3(Entity):
    
    email = Field(Unicode(254), required=True)
    person = ManyToOne('Person', required=True, ondelete='cascade')
    
    using_options(tablename="emails3")

class Email4(Entity):
    
    email = Field(Unicode(254), required=True)
    person = ManyToOne('Person', ondelete='cascade')
    
    using_options(tablename="emails4")