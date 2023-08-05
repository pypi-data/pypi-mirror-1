import unittest

from objectstatetracer.extension import start_extension, stop_extension, \
                                        ObjectStateTrace, register_class

from sqlobject import *

from turbogears import database, testutil, config

from datetime import datetime, date

config.update({'objectstatetracer.on': True})

hub = database.PackageHub('objectstatetracer.dburi')
__connection__ = hub

class Person(SQLObject):
    name = StringCol(length=50)
    age = IntCol()
    birthday = DateCol()
    picture = BLOBCol()
    likes_cake = BoolCol()

class Telephone(SQLObject):
    number = StringCol(length=15)
    person = ForeignKey('Person')

class Address(SQLObject):
    number = StringCol(length=15)
    person = ForeignKey('Person')

def test():
    
    Person.createTable()
    Telephone.createTable()
    Address.createTable()
    
    register_class(Person)
    register_class(Telephone)
    # we don't register address to test if it's being ignored by ost
    
    start_extension() # this is done automatically by TurboGears on apps.
    
    pic1 = open('objectstatetracer/static/images/tg_under_the_hood.png', 'rb')
    pic1 = pic1.read().encode('base64')
    
    pic2 = open('objectstatetracer/static/images/under_the_hood_blue.png', 'rb')
    pic2 = pic2.read().encode('base64')
    
    hub.begin()
    
    john = Person(name='John', age=30, birthday=date(2000,1,1), 
                  picture=pic1, likes_cake=True)
    john.name = 'Johnny'
    john.name = 'Johnny' # not a typo, testing that it skips a non update.
    john.set(name='John', age=20)
    john.birthday = date(2001,2,2)
    john.picture = pic2
    john.picture = pic1
    john.likes_cake = False
    john.likes_cake = True
    
    jane = Person(name='Jane', age=30, birthday=date(2000,1,1), picture=pic2,
                  likes_cake=True)
    
    phone = Telephone(number='12345', person=john)
    phone.person = jane
    phone.person = jane # not a typo, testing that it skips a non update.
    phone.personID = john.id
    phone.personID = john.id # not a typo, testing that it skips a non update.
    
    address = Address(number='12345', person=john)
    address.number = '1234'
    
    hub.commit()
    
    mod_history = john.get_modification_history()
    
    assert mod_history[0].old_value == 'John'
    assert mod_history[0].new_value == 'Johnny'
    
    assert mod_history[1].old_value != 'John'
    assert mod_history[1].new_value != 'Johnny'
    
    assert mod_history[1].old_value == 30
    assert mod_history[1].new_value == 20
    
    assert mod_history[2].old_value == 'Johnny'
    assert mod_history[2].new_value == 'John'
    
    assert mod_history[3].old_value == date(2000, 1, 1)
    assert mod_history[3].new_value == date(2001, 2, 2)
    
    assert mod_history[4].old_value == pic1
    assert mod_history[4].new_value == pic2
    
    assert mod_history[5].old_value == pic2
    assert mod_history[5].new_value == pic1
    
    assert mod_history[6].old_value
    assert not mod_history[6].new_value
    
    assert not mod_history[7].old_value
    assert mod_history[7].new_value
    
    mod_history = phone.get_modification_history()
    
    assert mod_history[0].old_value == 1
    assert mod_history[0].new_value == 2
    assert mod_history[0].column_name == 'personID'
    
    assert mod_history[1].old_value != 1
    assert mod_history[1].new_value != 2
    assert mod_history[1].column_name == 'personID'
    
    assert mod_history[1].old_value == 2
    assert mod_history[1].new_value == 1
    assert mod_history[1].column_name == 'personID'
    
    assert mod_history.count() == 2
    
    assert address.get_modification_history().count() == 0
    
    stop_extension()

