# -*- coding: utf-8 -*-

import unittest
import cherrypy

from objectstatetracer.extension import ObjectStateTrace, register_class
from objectstatetracer.auth import AuthSchema

from sqlobject import *

import turbogears
from turbogears import database, testutil, config, identity
from turbogears.identity.soprovider import TG_User, TG_Group

from datetime import datetime, date

from nose import with_setup

from exceptions import *

config.update({'objectstatetracer.on': True})
config.update({'visit.on': True})
config.update({'identity.on': True})

hub = database.PackageHub('objectstatetracer.dburi')
__connection__ = hub

class Person(SQLObject):
    name = StringCol(length=50)
    age = IntCol()
    birthday = DateCol()
    picture = BLOBCol()
    likes_cake = BoolCol()
    credits = MultipleJoin('Credit')
    loans = MultipleJoin('Loan')

class Telephone(SQLObject):
    number = StringCol(length=15)
    person = ForeignKey('Person')

class Address(SQLObject):
    number = StringCol(length=15)
    person = ForeignKey('Person')

class Credit(SQLObject):
    person = ForeignKey('Person')
    amount = FloatCol()

class Loan(SQLObject):
    person = ForeignKey('Person')
    amount = FloatCol()

class UnicodePerson(SQLObject):
    name = UnicodeCol(length=50)

Person.createTable()
UnicodePerson.createTable()
Telephone.createTable()
Address.createTable()
Credit.createTable()
Loan.createTable()

register_class(Person)
register_class(UnicodePerson)
register_class(Telephone)
# we don't register address to test if it's being ignored by ost
auth_schema = AuthSchema(modify=identity.in_group('admins'),
                         modify_pending=identity.not_anonymous(),
                         authorize_modification=identity.in_group('admins'))
register_class(Credit, auth_schema=auth_schema)
auth_schema = AuthSchema(modify=identity.in_group('admins'),
                         modify_pending=identity.not_anonymous(),
                         authorize_modification=identity.in_group('admins'),
                         min_approves_needed=3, min_rejects_needed=3)
register_class(Loan, auth_schema=auth_schema)

class DummyRoot(object):
    def index(self):
        return 'Test'
    index.exposed = True

cherrypy.root = DummyRoot()

def set_user(user):
    if not user:
        cherrypy.request.identity = \
            identity.current_provider.anonymous_identity()
    cherrypy.request.identity = \
        identity.current_provider.authenticated_identity(user)

def teardown_func():
    turbogears.startup.stopTurboGears()

testutil.createRequest('/')
teardown_func()

admins = TG_Group(group_name='admins', display_name='Administrators')

user = TG_User(user_name='test_user', display_name='Test User',
               email_address='k@kw.com', password='123456')

admin1 = TG_User(user_name='admin1', display_name='Admin User 1',
                 email_address='kwww@kw1.com', password='123456')
admins.addTG_User(admin1)

admin2 = TG_User(user_name='admin2', display_name='Admin User 2',
                 email_address='kwww@kw2.com', password='123456')
admins.addTG_User(admin2)

admin3 = TG_User(user_name='admin3', display_name='Admin User 3',
                 email_address='kwww@kw3.com', password='123456')
admins.addTG_User(admin3)

pic1 = open('objectstatetracer/static/images/tg_under_the_hood.png', 'rb')
pic1 = pic1.read()

pic2 = open('objectstatetracer/static/images/under_the_hood_blue.png', 'rb')
pic2 = pic2.read()

john = Person(name='John', age=30, birthday=date(2000,1,1), 
              picture=pic1, likes_cake=True)

jane = Person(name='Jane', age=30, birthday=date(2000,1,1), picture=pic2,
              likes_cake=True)
    
set_user(admin1)
Credit(amount=1000, person=john)
Loan(amount=1000, person=john)


@with_setup(teardown=teardown_func)
def test_01_tracing():
    """
    Tests that OST is saving the change history correctly.
    """
    
    set_user(None)
    
    john.name = 'Johnny'
    john.name = 'Johnny' # not a typo, testing that it skips a non update.
    john.set(name='John', age=20)
    john.birthday = date(2001,2,2)
    john.picture = pic2
    john.picture = pic1
    john.likes_cake = False
    john.likes_cake = True
    
    set_user(user)
    
    phone = Telephone(number='12345', person=john)
    phone.person = jane
    phone.person = jane # not a typo, testing that it skips a non update.
    phone.personID = john.id
    phone.personID = john.id # not a typo, testing that it skips a non update.
    
    address = Address(number='12345', person=john)
    address.number = '1234'
    
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
    
    for state in mod_history:
        assert state.user == None, 'User set, expected None'
    
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
    
    for state in mod_history:
        assert state.user == user, 'No User set'
    
    assert address.get_modification_history().count() == 0

@with_setup(teardown=teardown_func)
def test_02_no_permission():
    """
    Tests that users without write or write_pending permissions can't write on
    protected classes.
    """
    old_value = john.credits[0].amount
    set_user(None)
    try:
        john.credits[0].amount += 1000
        assert False, 'Anonymous users shouldn\'t be able to modify'
    except PermissionError, e:
        assert john.credits[0].amount == old_value, \
               'Change with PermissionError went through'

@with_setup(teardown=teardown_func)
def test_03_pending_write():
    """
    Tests that users with write_pending permission generate pending writes.
    """
    old_value = john.credits[0].amount
    set_user(user)
    try:
        john.credits[0].amount += 1000
    except PermissionError, e:
        assert False, 'PermissionError when the change should be pending'
    assert john.credits[0].amount == old_value, \
           'The write was done when it should be pending'
    pending_changes = john.credits[0].get_pending_changes()
    assert pending_changes.count() == 1, \
           'Expected 1, got %i' % pending_changes.count()
    assert pending_changes[0].old_value == old_value
    assert pending_changes[0].new_value == old_value + 1000

@with_setup(teardown=teardown_func)
def test_04_authorization():
    """
    Tests that users with authorization permission can approve changes.
    We are going to authorize the change we did in test_03.
    """
    set_user(admin1)
    
    old_value = john.credits[0].amount
    pending_changes = john.credits[0].get_pending_changes()
    new_value = pending_changes[0].new_value
    
    pending_changes[0].approve()
    assert pending_changes.count() == 0, \
           'Approving should clear the pending change'
    
    mod_history = john.credits[0].get_modification_history()
    assert mod_history.count() == 1, 'The change wasn\'t traced'
    assert mod_history[0].old_value == old_value
    assert mod_history[0].new_value == new_value
    
    assert john.credits[0].amount == new_value, 'The change wasn\'t written' 
    
    assert len(mod_history[0].approves) == 1
    assert admin1 in [i.user for i in mod_history[0].approves]
    assert admin2 not in [i.user for i in mod_history[0].approves]
    assert len(mod_history[0].rejects) == 0

@with_setup(teardown=teardown_func)
def test_05_denied_anonymous_authorization():
    """
    Tests that users without authorization permission can't approve changes.
    """
    old_value = john.credits[0].amount
    test_03_pending_write()
    
    set_user(None)
    pending = john.credits[0].get_pending_changes()
    try:
        pending[0].approve()
        assert False, 'Anonymous users should not be able to approve'
    except PermissionError:
        assert john.credits[0].amount == old_value, 'Change went through'
    
    set_user(user)
    try:
        pending[0].approve()
        assert False, 'Non authorized users should not be able to approve'
    except PermissionError:
        assert john.credits[0].amount == old_value, 'Change went through'

@with_setup(teardown=teardown_func)
def test_06_pending_write_on_multiple():
    """
    Tests that users with write_pending permission generate pending writes on
    classes that need multiple approves
    """
    old_value = john.loans[0].amount
    set_user(user)
    try:
        john.loans[0].amount += 1000
    except PermissionError, e:
        assert False, 'PermissionError when the change should be pending'
    assert john.loans[0].amount == old_value, \
           'The write was done when it should be pending'
    pending_changes = john.loans[0].get_pending_changes()
    assert pending_changes.count() == 1, \
           'Expected 1, got %i' % pending_changes.count()
    assert pending_changes[0].old_value == old_value
    assert pending_changes[0].new_value == old_value + 1000

@with_setup(teardown=teardown_func)
def test_07_multiple_authorization():
    """
    Test that pending changes need the right amount of approves to be written.
    """
    old_value = john.loans[0].amount
    pending_changes = john.loans[0].get_pending_changes()
    new_value = pending_changes[0].new_value
    
    assert pending_changes.count() == 1, \
           'Something went wrong preparing the test'
    
    # 1st approve
    set_user(admin1)
    pending_changes[0].approve()
    assert pending_changes.count() == 1, \
           '1 approve shouldn\'t clear the pending change, 2 more were needed'
    assert len(pending_changes[0].approves) == 1
    assert john.loans[0].amount == old_value, 'Change went through'
    
    try:
        pending_changes[0].approve()
        assert False, '2nd approve by the same user should raise a ' \
                      'PermissionError'
    except PermissionError:
        assert len(pending_changes[0].approves) == 1, \
               'Extra approve went through'
        assert john.loans[0].amount == old_value, 'Change went through'
    
    # 2nd approve
    set_user(admin2)
    pending_changes[0].approve()
    assert pending_changes.count() == 1, \
           '2 approves shouldn\'t clear the pending change, 1 more was needed'
    assert len(pending_changes[0].approves) == 2
    assert john.loans[0].amount == old_value, 'Change went through'
    
    try:
        pending_changes[0].approve()
        assert False, '2nd approve by the same user should raise a ' \
                      'PermissionError'
    except PermissionError:
        assert len(pending_changes[0].approves) == 2, \
               'Extra approve went through'
        assert john.loans[0].amount == old_value, 'Change went through'
    
    # 3rd and last approve
    set_user(admin3)
    pending_changes[0].approve()
    assert pending_changes.count() == 0, \
           '3 approves should clear the pending change'
    
    mod_history = john.loans[0].get_modification_history()
    assert mod_history.count() == 1, 'The change wasn\'t traced'
    assert mod_history[0].old_value == old_value
    assert mod_history[0].new_value == new_value
    
    assert john.loans[0].amount == new_value, 'The change wasn\'t written' 
    
    assert len(mod_history[0].approves) == 3
    assert admin1 in [i.user for i in mod_history[0].approves]
    assert admin2 in [i.user for i in mod_history[0].approves]
    assert admin3 in [i.user for i in mod_history[0].approves]
    assert len(mod_history[0].rejects) == 0

@with_setup(teardown=teardown_func)
def test_08_denied_anonymous_reject():
    """
    Tests that users without authorization permission can't reject changes.
    """
    if john.credits[0].get_pending_changes().count() < 1:
        test_03_pending_write()
    
    old_value = john.credits[0].amount
    
    set_user(None)
    pending = john.credits[0].get_pending_changes()
    old_reject_count = john.credits[0].get_rejected_changes().count()
    
    try:
        pending[0].reject()
        assert False, 'Anonymous users should not be able to reject'
    except PermissionError:
        assert john.credits[0].amount == old_value, 'Change went through'
    
    set_user(user)
    try:
        pending[0].reject()
        assert False, 'Non authorized users should not be able to reject'
    except PermissionError:
        assert john.credits[0].amount == old_value, 'Change went through'
    
    rejected_changes = john.credits[0].get_rejected_changes()
    assert old_reject_count == rejected_changes.count(), \
           'A rejection was saved'

@with_setup(teardown=teardown_func)
def test_09_reject():
    """
    Tests that users with authorization permission can reject changes.    
    """
    if john.credits[0].get_pending_changes().count() < 1:
        test_03_pending_write()
    
    set_user(admin1)
    
    old_value = john.credits[0].amount
    pending_changes = john.credits[0].get_pending_changes()
    new_value = pending_changes[0].new_value
    old_mod_history_count = john.credits[0].get_modification_history().count()
    old_reject_count = john.credits[0].get_rejected_changes().count()
    
    pending_changes[0].reject()
    assert pending_changes.count() == 0, \
           'Rejecting should clear the pending change'
    
    mod_history = john.credits[0].get_modification_history()
    assert mod_history.count() == old_mod_history_count, \
           'A reject shouldn\'t be saved as a trace'
    
    assert john.credits[0].amount == old_value, 'The change was written' 
    
    rejected_changes = john.credits[0].get_rejected_changes()
    assert rejected_changes.count() == old_reject_count + 1, \
           'There should be a new rejection'
    
    last_rejected = rejected_changes[-1]
    assert len(last_rejected.approves) == 0
    assert len(last_rejected.rejects) == 1
    assert admin1 in [i.user for i in last_rejected.rejects]

@with_setup(teardown=teardown_func)
def test_10_multiple_reject():
    """
    Test that pending changes need the right amount of rejects to be rejected.
    """
    if john.loans[0].get_pending_changes().count() < 1:
        test_06_pending_write_on_multiple()
    
    set_user(admin1)
    
    old_value = john.loans[0].amount
    pending_changes = john.loans[0].get_pending_changes()
    new_value = pending_changes[0].new_value
    pending_changes_count = john.loans[0].get_pending_changes().count()
    old_mod_history_count = john.loans[0].get_modification_history().count()
    old_reject_count = john.loans[0].get_rejected_changes().count()
    pending_change = pending_changes[0]
    
    # 1st reject
    set_user(admin1)
    pending_change.reject()
    assert pending_changes.count() == pending_changes_count, \
           '1 reject shouldn\'t clear the pending change, 2 more were needed'
    assert len(pending_change.rejects) == 1
    assert john.loans[0].amount == old_value, 'Change went through'
    
    try:
        pending_change.reject()
        assert False, '2nd reject by the same user should raise a ' \
                      'PermissionError'
    except PermissionError:
        assert len(pending_change.rejects) == 1, \
               'Extra reject went through'
        assert john.loans[0].amount == old_value, 'Change went through'
    
    # 2nd reject
    set_user(admin2)
    pending_change.reject()
    assert pending_changes.count() == pending_changes_count, \
           '2 rejects shouldn\'t clear the pending change, 1 more was needed'
    assert len(pending_change.rejects) == 2
    assert john.loans[0].amount == old_value, 'Change went through'
    
    try:
        pending_change.reject()
        assert False, '2nd reject by the same user should raise a ' \
                      'PermissionError'
    except PermissionError:
        assert len(pending_change.rejects) == 2, \
               'Extra reject went through'
        assert john.loans[0].amount == old_value, 'Change went through'
    
    # 3rd and last reject
    set_user(admin3)
    pending_change.reject()
    assert pending_changes.count() == pending_changes_count - 1, \
           '3 rejects should clear the pending change'
    
    rejected_change = john.loans[0].get_history()[-1]
    assert rejected_change == pending_change
    assert rejected_change.old_value == old_value
    assert rejected_change.new_value == new_value
    
    assert john.loans[0].amount == old_value, 'The change was written' 
    
    assert len(rejected_change.rejects) == 3
    assert admin1 in [i.user for i in rejected_change.rejects]
    assert admin2 in [i.user for i in rejected_change.rejects]
    assert admin3 in [i.user for i in rejected_change.rejects]
    assert len(rejected_change.approves) == 0

tito = UnicodePerson(name='Tito')
@with_setup(teardown=teardown_func)
def test_11_unicode():
    tito.name = u'Títö'
    assert tito.get_modification_history()[0].new_value == u'Títö'

@with_setup(teardown=teardown_func)
def test_12_states():
    set_user(None)
    
    john._states['authorized'] = True
    
    assert john._states.keys() == ['authorized']
    assert john._states['authorized'] is True
    
    try:
        john._states['qweqwe']
        assert False, 'Invalid key should raise KeyError'
    except KeyError:
        pass
    
    assert john._states.has_key('authorized') is True
    assert john._states.has_key('qweqwe') is False
    
    assert john._states.get_history('authorized').count() == 0
    
    john._states['authorized'] = False
    assert john._states['authorized'] is False
    assert john._states.get_history('authorized').count() == 1

@with_setup(teardown=teardown_func)
def test_13_state_no_permission():
    """
    Tests that users without write or write_pending permissions can't write on
    protected classes states.
    """
    set_user(admin1)
    old_value = john.credits[0]._states['blocked'] = False 
    
    set_user(None)
    
    try:
        john.credits[0]._states['blocked'] = True
        assert False, 'Anonymous users shouldn\'t be able to modify'
    except PermissionError, e:
        assert john.credits[0]._states['blocked'] is old_value, \
               'Change with PermissionError went through'

@with_setup(teardown=teardown_func)
def test_14_state_pending_change():
    """
    Tests that users with write_pending permission generate pending writes on
    status changes.
    """
    set_user(user)
    cs =  john.credits[0]._states
    old_pending_count =  cs.get_pending_changes('blocked').count()
    old_value = cs['blocked']
    try:
        cs['blocked'] = not old_value
    except PermissionError, e:
        assert False, 'PermissionError when the change should be pending'
    assert cs['blocked'] == old_value, \
           'The write was done when it should be pending'
    pending_changes = cs.get_pending_changes('blocked')
    assert pending_changes.count() == old_pending_count + 1, \
           'Expected %i, got %i' % (old_pending_count + 1,
                                    pending_changes.count())
    assert pending_changes[0].old_value is old_value
    assert pending_changes[0].new_value is not old_value

@with_setup(teardown=teardown_func)
def test_15_state_authorization():
    cs =  john.credits[0]._states
    
    if cs.get_pending_changes('blocked').count() < 1:
        test_14_state_pending_change()
    
    set_user(admin1)
    
    old_pending_count =  cs.get_pending_changes('blocked').count()
    old_mod_count = cs.get_modification_history('blocked').count()
    old_value =  cs['blocked']
    
    pending_changes = cs.get_pending_changes('blocked')
    pending = pending_changes[-1]
    
    pending.approve()
    
    mod_history = cs.get_modification_history('blocked')
    
    assert pending_changes.count() == old_pending_count - 1
    assert mod_history.count() == old_mod_count + 1
    assert pending == mod_history[-1]
    assert pending.old_value == old_value
    assert pending.new_value == cs['blocked']
    assert cs['blocked'] != old_value
    assert pending not in list(cs.get_pending_changes('blocked'))
    assert admin1 in [i.user for i in pending.approves]
    assert admin2 not in [i.user for i in pending.approves]
    

@with_setup(teardown=teardown_func)
def test_16_state_rejection():
    cs =  john.credits[0]._states
    
    if cs.get_pending_changes('blocked').count() < 1:
        test_14_state_pending_change()
    
    set_user(admin1)
    
    old_rejected_count =  cs.get_rejected_changes('blocked').count()
    old_pending_count =  cs.get_pending_changes('blocked').count()
    old_mod_count = cs.get_modification_history('blocked').count()
    old_value =  cs['blocked']
    
    pending_changes = cs.get_pending_changes('blocked')
    pending = pending_changes[-1]
    
    pending.reject()
    
    rejected_changes = cs.get_rejected_changes('blocked')
    rejected = rejected_changes[-1]
    mod_history = cs.get_modification_history('blocked')
    
    assert pending_changes.count() == old_pending_count - 1
    assert rejected_changes.count() == old_rejected_count + 1
    assert mod_history.count() == old_mod_count
    assert cs['blocked'] == old_value
    assert pending not in list(mod_history)
    assert pending in list(rejected_changes)
    assert admin1 in [i.user for i in pending.rejects]
    assert admin2 not in [i.user for i in pending.rejects]

@with_setup(teardown=teardown_func)
def test_17_trace_missing_fkey():
    phone = Telephone(number='12345', person=john)
    try:
        phone.personID = 100
        phone.person = john
        phone.personID = 100
        phone.personID = john.id
        phone.set(personID=100)
        phone.set(person=john)
        phone.set(personID=100)
        phone.set(personID=john.id)
    except SQLObjectNotFound:
        assert False, 'Error while tracing a non existant foreign key'

# FIXME agregar un testeo de pending change con SET (

# FIXME testear que un set no genere pendings por cambios nulos

# FIXME testear que un setattr no genere pendings por cambios nulos

# FIXME agregar un testeo de que alguien sin escritura pendiente pero con 
# escritura inmediata, pueda escribir (se corrigio un bug donde el no tener
# escritura pendiente hacia que se corte la modificacion

# FIXME agregar un test que cambie una fecha de nula a algo
# actualmente la fecha nueva se guardaria con la hora en el state
# al no tener para comparar no sabe que es date y no datetime.

# FIXME agregar un testeo del controller OST (corroborar permisos/accesos)

