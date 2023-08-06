# -*- coding: utf-8 -*-

import unittest
import cherrypy
import threading
import time
import os

from objectstatetracer.extension import ObjectStateTrace, register_class
from objectstatetracer.model import TraceData
from objectstatetracer.state import ObjectState
from objectstatetracer.auth import AuthSchema
from objectstatetracer.controllers import HistoryController

from sqlobject import *

import turbogears
from turbogears import database, testutil, config, identity
from turbogears.identity.soprovider import TG_User, TG_Group

from datetime import datetime, date

from nose import with_setup

from exceptions import *

hub = database.PackageHub('sqlobject.dburi')
__connection__ = hub

class Person(SQLObject):
    name = StringCol(length=50)
    age = IntCol()
    birthday = DateCol()
    picture = BLOBCol(length=1024 ** 2)
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


class FriendShip(SQLObject):
    person_1 = ForeignKey('Person')
    person_2 = ForeignKey('Person')
    
    def _set_person_2ID(self, value):
        return self._SO_set_person_2ID(value)


class UnicodePerson(SQLObject):
    name = UnicodeCol(length=50, alternateID=True)


def init_cherrypy():
    config.update({'objectstatetracer.on': True})
    config.update({'visit.on': True})
    config.update({'identity.on': True})
    config.update({'autoreload.on': False})
    
    class DummyRoot(object):
        def index(self):
            return 'Test'
        index.exposed = True
        
        history = HistoryController()

    cherrypy.root = DummyRoot()
    cherrypy.root.started = True
    testutil.createRequest('/')

def set_user(user):
    user = user and TG_User.get(user.id)
    if not user:
        cherrypy.request.identity = \
            identity.current_provider.anonymous_identity()
    cherrypy.request.identity = \
        identity.current_provider.authenticated_identity(user)

def with_transaction(func):
    def wrapped(*args, **kw):
        hub.begin()
        try:
            try:
                output = func(*args, **kw)
                hub.commit()
                return output
            except:
                hub.rollback()
                raise
        finally:
            hub.end()
    wrapped.__name__ = func.__name__
    return wrapped

def assert_equals(value_1, value_2, msg=None):
    if msg is None:
        msg = '%s == %s' % (value_1, value_2)
    assert value_1 == value_2, msg

def assert_not_equals(value_1, value_2, msg=None):
    if msg is None:
        msg = '%s != %s' % (value_1, value_2)
    assert value_1 != value_2, msg

conn = hub.getConnection()
conn.query('DROP TABLE IF EXISTS loan')
conn.query('DROP TABLE IF EXISTS credit')
conn.query('DROP TABLE IF EXISTS address')
conn.query('DROP TABLE IF EXISTS telephone')
conn.query('DROP TABLE IF EXISTS friend_ship')
conn.query('DROP TABLE IF EXISTS unicode_person')
conn.query('DROP TABLE IF EXISTS person')
conn.query('DROP TABLE IF EXISTS tg_permission')
conn.query('DROP TABLE IF EXISTS tg_group_permission')
conn.query('DROP TABLE IF EXISTS tg_group')
conn.query('DROP TABLE IF EXISTS tg_user_group')
conn.query('DROP TABLE IF EXISTS tg_user')
conn.query('DROP TABLE IF EXISTS tg_visit_identity')
conn.query('DROP TABLE IF EXISTS tg_visit')
conn.query('DROP TABLE IF EXISTS ost_trace_data')
conn.query('DROP TABLE IF EXISTS ost_states')
conn.query('DROP TABLE IF EXISTS ost_approves')
conn.query('DROP TABLE IF EXISTS ost_rejects')
conn.query('DROP TABLE IF EXISTS ost_main')

Person.createTable()
UnicodePerson.createTable()
Telephone.createTable()
Address.createTable()
Credit.createTable()
Loan.createTable()
FriendShip.createTable()

register_class(Person)
register_class(Telephone)
register_class(FriendShip)

# we don't register address to test if it's being ignored by ost
auth_schema = AuthSchema(modify=identity.in_group('admins'),
                         modify_pending=identity.not_anonymous(),
                         authorize_modification=identity.in_group('admins'),
                         create=identity.in_group('superadmins'),
                         create_pending=identity.not_anonymous(),
                         authorize_creation=identity.in_group('admins'))
register_class(Credit, auth_schema=auth_schema)
register_class(UnicodePerson, auth_schema=auth_schema)
auth_schema = AuthSchema(modify=identity.in_group('admins'),
                         modify_pending=identity.not_anonymous(),
                         authorize_modification=identity.in_group('admins'),
                         create=identity.in_group('admins'),
                         create_pending=identity.not_anonymous(),
                         authorize_creation=identity.in_group('admins'),
                         min_approves_needed=3, min_rejects_needed=3)
register_class(Loan, auth_schema=auth_schema)

init_cherrypy()

hub.begin()
admins = TG_Group(group_name='admins', display_name='Administrators')
sadmins = TG_Group(group_name='superadmins', display_name='SAdministrators')

user = TG_User(user_name='test_user', display_name='Test User',
               email_address='k@kw.com', password='123456')

admin1 = TG_User(user_name='admin1', display_name='Admin User 1',
                 email_address='kwww@kw1.com', password='123456')
admins.addTG_User(admin1)
sadmins.addTG_User(admin1)

admin2 = TG_User(user_name='admin2', display_name='Admin User 2',
                 email_address='kwww@kw2.com', password='123456')
admins.addTG_User(admin2)

admin3 = TG_User(user_name='admin3', display_name='Admin User 3',
                 email_address='kwww@kw3.com', password='123456')
admins.addTG_User(admin3)

pic1 = open('objectstatetracer/static/images/tg_under_the_hood.png', 'rb')
pic1 = pic1.read().encode('base64')

pic2 = open('objectstatetracer/static/images/under_the_hood_blue.png', 'rb')
pic2 = pic2.read().encode('base64')

john = Person(name='John', age=30, birthday=date(2000,1,1), 
              picture=pic1, likes_cake=True)
john_id = john.id

jane = Person(name='Jane', age=30, birthday=date(2000,1,1), picture=pic2,
              likes_cake=True)
jane_id = jane.id

set_user(admin1)
Credit(amount=1000, person=john)
Loan(amount=1000, person=john)

tito = UnicodePerson(name='Tito')
tito_id = tito.id

friendship = FriendShip(person_1=john, person_2=jane)

hub.commit()
hub.end()

@with_transaction
def test_01_tracing():
    """
    Tests that OST is saving the change history correctly.
    """
    
    set_user(None)
    
    john = Person.get(john_id)
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
    address.set(number='123456')
    
    mod_history = john.get_modification_history()
    
    assert mod_history[0]['name'].old_value is None
    assert mod_history[0]['name'].new_value == 'John'
    
    assert mod_history[1]['name'].old_value == 'John'
    assert mod_history[1]['name'].new_value == 'Johnny'
    
    assert mod_history[2]['name'].old_value != 'John'
    assert mod_history[2]['name'].new_value != 'Johnny'
    
    assert mod_history[2]['name'].old_value == 'Johnny'
    assert mod_history[2]['name'].new_value == 'John'
    
    assert mod_history[2]['age'].old_value == 30
    assert mod_history[2]['age'].new_value == 20
    
    assert mod_history[3]['birthday'].old_value == date(2000, 1, 1)
    assert mod_history[3]['birthday'].new_value == date(2001, 2, 2)
    
    assert mod_history[4]['picture'].old_value == pic1
    assert mod_history[4]['picture'].new_value == pic2
    
    assert mod_history[5]['picture'].old_value == pic2
    assert mod_history[5]['picture'].new_value == pic1
    
    assert mod_history[6]['likes_cake'].old_value
    assert not mod_history[6]['likes_cake'].new_value
    
    assert not mod_history[7]['likes_cake'].old_value
    assert mod_history[7]['likes_cake'].new_value
    
    for state in john.get_modification_history():
        assert state.user == None, 'User set, expected None'
    
    mod_history = phone.get_modification_history()
    
    assert mod_history[0]['personID'].old_value == None
    assert mod_history[0]['personID'].new_value == 1
    
    assert mod_history[1]['personID'].old_value == 1
    assert mod_history[1]['personID'].new_value == 2
    
    assert mod_history[2]['personID'].old_value != 1
    assert mod_history[2]['personID'].new_value != 2
    
    assert mod_history[2]['personID'].old_value == 2
    assert mod_history[2]['personID'].new_value == 1
    
    assert mod_history.count() == 3
    
    for state in phone.get_modification_history():
        assert state.user.id == user.id, 'No User set'
    
    assert address.get_modification_history().count() == 0

@with_transaction
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

@with_transaction
def test_03_pending_write():
    """
    Tests that users with write_pending permission generate pending writes.
    """
    old_value = john.credits[0].amount
    old_pending_count = john.credits[0].get_pending_changes().count()
    set_user(user)
    try:
        john.credits[0].amount += 1000
    except PermissionError, e:
        assert False, 'PermissionError when the change should be pending'
    except PendingChange, e:
        pass
    assert john.credits[0].amount == old_value, \
           'The write was done when it should be pending'
    pending_changes = john.credits[0].get_pending_changes()
    assert pending_changes[-1] == e.args[1]
    assert pending_changes.count() == old_pending_count + 1, \
           'Expected %i, got %i' % (old_pending_count + 1, 
                                    pending_changes.count())
    assert pending_changes[-1]['amount'].old_value == old_value
    assert pending_changes[-1]['amount'].new_value == old_value + 1000

@with_transaction
def test_04_authorization():
    """
    Tests that users with authorization permission can approve changes.
    We are going to authorize the change we did in test_03.
    """
    set_user(admin1)
    
    old_value = john.credits[0].amount
    pending_changes = john.credits[0].get_pending_changes()
    old_mod_history_count = john.credits[0].get_modification_history().count()
    new_value = pending_changes[0]['amount'].new_value
    
    pending_changes[0].approve()
    assert pending_changes.count() == 0, \
           'Approving should clear the pending change'
    
    mod_history = john.credits[0].get_modification_history()
    assert mod_history.count() == old_mod_history_count + 1, \
            'The change wasn\'t traced'
    assert mod_history[1]['amount'].old_value == old_value
    assert mod_history[1]['amount'].new_value == new_value
    
    assert john.credits[0].amount == new_value, 'The change wasn\'t written' 
    
    assert len(mod_history[1].approves) == 1
    assert admin1.id in [i.user.id for i in mod_history[1].approves]
    assert admin2.id not in [i.user.id for i in mod_history[1].approves]
    assert len(mod_history[1].rejects) == 0

@with_transaction
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

@with_transaction
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
    except PendingChange, e:
        pass
    assert john.loans[0].amount == old_value, \
           'The write was done when it should be pending'
    pending_changes = john.loans[0].get_pending_changes()
    assert pending_changes[-1] == e.args[1]
    assert pending_changes.count() == 1, \
           'Expected 1, got %i' % pending_changes.count()
    assert pending_changes[0]['amount'].old_value == old_value
    assert pending_changes[0]['amount'].new_value == old_value + 1000

@with_transaction
def test_07_multiple_authorization():
    """
    Test that pending changes need the right amount of approves to be written.
    """
    old_value = john.loans[0].amount
    old_mod_history_count = john.loans[0].get_modification_history().count()
    pending_changes = john.loans[0].get_pending_changes()
    new_value = pending_changes[0]['amount'].new_value
    
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
    assert mod_history.count() == old_mod_history_count + 1, \
            'The change wasn\'t traced'
    assert mod_history[1]['amount'].old_value == old_value
    assert mod_history[1]['amount'].new_value == new_value
    
    assert john.loans[0].amount == new_value, 'The change wasn\'t written' 
    
    assert len(mod_history[1].approves) == 3
    assert admin1.id in [i.user.id for i in mod_history[1].approves]
    assert admin2.id in [i.user.id for i in mod_history[1].approves]
    assert admin3.id in [i.user.id for i in mod_history[1].approves]
    assert len(mod_history[1].rejects) == 0

@with_transaction
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

@with_transaction
def test_09_reject():
    """
    Tests that users with authorization permission can reject changes.    
    """
    if john.credits[0].get_pending_changes().count() < 1:
        test_03_pending_write()
    
    set_user(admin1)
    
    old_value = john.credits[0].amount
    pending_changes = john.credits[0].get_pending_changes()
    new_value = pending_changes[0]['amount'].new_value
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
    assert admin1.id in [i.user.id for i in last_rejected.rejects]

@with_transaction
def test_10_multiple_reject():
    """
    Test that pending changes need the right amount of rejects to be rejected.
    """
    if john.loans[0].get_pending_changes().count() < 1:
        test_06_pending_write_on_multiple()
    
    set_user(admin1)
    
    old_value = john.loans[0].amount
    pending_changes = john.loans[0].get_pending_changes()
    new_value = pending_changes[0]['amount'].new_value
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
    assert rejected_change['amount'].old_value == old_value
    assert rejected_change['amount'].new_value == new_value
    
    assert john.loans[0].amount == old_value, 'The change was written' 
    
    assert len(rejected_change.rejects) == 3
    assert admin1.id in [i.user.id for i in rejected_change.rejects]
    assert admin2.id in [i.user.id for i in rejected_change.rejects]
    assert admin3.id in [i.user.id for i in rejected_change.rejects]
    assert len(rejected_change.approves) == 0
    
    assert john.loans[0].get_modification_history().count() == \
            old_mod_history_count

@with_transaction
def test_11_unicode():
    set_user(admin1)
    tito = UnicodePerson.get(tito_id)
    try:
        tito.name = u'Títö'
    except PendingChange, e:
        pass
    assert tito.get_modification_history()[-1]['name'].new_value == u'Títö'

@with_transaction
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

@with_transaction
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

@with_transaction
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
    except PendingChange, e:
        pass
    assert cs['blocked'] == old_value, \
           'The write was done when it should be pending'
    pending_changes = cs.get_pending_changes('blocked')
    assert pending_changes[-1] == e.args[1]
    assert pending_changes.count() == old_pending_count + 1, \
           'Expected %i, got %i' % (old_pending_count + 1,
                                    pending_changes.count())
    assert pending_changes[0]['value'].old_value is old_value
    assert pending_changes[0]['value'].new_value is not old_value

@with_transaction
def test_15_state_authorization():
    cs =  john.credits[0]._states
    
    if cs.get_pending_changes('blocked').count() < 1:
        test_14_state_pending_change()
    
    old_pending_count =  cs.get_pending_changes('blocked').count()
    old_mod_count = cs.get_modification_history('blocked').count()
    old_value =  cs['blocked']
    
    set_user(admin1)
    
    pending_changes = cs.get_pending_changes('blocked')
    pending = pending_changes[-1]
    
    pending.approve()
    
    mod_history = cs.get_modification_history('blocked')
    
    assert pending_changes.count() == old_pending_count - 1
    assert mod_history.count() == old_mod_count + 1
    assert pending == mod_history[-1]
    assert pending['value'].old_value == old_value
    assert pending['value'].new_value == cs['blocked']
    assert cs['blocked'] != old_value
    assert pending not in list(cs.get_pending_changes('blocked'))
    assert admin1.id in [i.user.id for i in pending.approves]
    assert admin2.id not in [i.user.id for i in pending.approves]

@with_transaction
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
    assert admin1.id in [i.user.id for i in pending.rejects]
    assert admin2.id not in [i.user.id for i in pending.rejects]

'''
@with_transaction
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
'''

@with_transaction
def test_18_prohibited_creation_test():
    set_user(None)
    old_credit_count = len(john.credits)
    try:
        credit = Credit(amount=10000000, person=john)
        assert False, 'Anonymous users shouldn\'t be able to create credits'
    except PermissionError, e:
        pass
    except PendingCreation, e:
        assert False, 'Anonymous users shouldn\'t be able to create credits'
    assert Credit.selectBy(personID=john.id).count() == old_credit_count, \
        'Creation went through'

@with_transaction
def test_19_pending_creation_test():
    set_user(user)
    old_credit_count = len(john.credits)
    old_creation_count = Credit.get_pending_creations().count()
    try:
        credit = Credit(amount=10000000, person=john)
        assert False, 'Users shouldn\'t be able to create credits'
    except PermissionError, e:
        assert False, 'Users should be able to create pending credits'
    except PendingCreation, e:
        pass
    assert Credit.selectBy(personID=john.id).count() == old_credit_count, \
        'Creation went through'
    assert Credit.get_pending_creations().count() == old_creation_count + 1, \
        'Pending creation not saved'

@with_transaction
def test_20_pending_creation_authorization_test():
    """
    Tests that we can authorize a pending object creation. Also tests
    that the right privileges are needed.
    Uses the pending creation from test_19.
    """
    old_credit_count = len(john.credits)
    old_creation_count = Credit.get_pending_creations().count()
    pending_credit = Credit.get_pending_creations()[-1]
    
    set_user(None)
    try:
        pending_credit.approve()
        assert False, 'Anonymous users shouldn\'t be able to approve'
    except PermissionError, e:
        pass
    assert Credit.selectBy(personID=john.id).count() == old_credit_count
    assert Credit.get_pending_creations().count() == old_creation_count
    
    set_user(user)
    try:
        pending_credit.approve()
        assert False, 'Users shouldn\'t be able to approve'
    except PermissionError, e:
        pass
    assert Credit.selectBy(personID=john.id).count() == old_credit_count
    assert Credit.get_pending_creations().count() == old_creation_count
    
    # admin2 can auth but can't write by himself but the write should be done
    # anyway.
    set_user(admin2)
    try:
        pending_credit.approve()
    except PermissionError, e:
        assert False, 'Authorized users should be able to approve'
    assert Credit.selectBy(personID=john.id).count() == old_credit_count + 1, \
        'Object wasn\'t written'
    assert Credit.get_pending_creations().count() == old_creation_count - 1, \
        'Pending creation still there'
    new_credit = Credit.select()[-1]
    mod_history = new_credit.get_modification_history()
    assert pending_credit is mod_history[0]
    assert mod_history[0].user.id == user.id
    assert mod_history.count() == 1
    assert new_credit.id == mod_history[0].instance_id
    assert new_credit.amount == mod_history[0]['amount'].new_value

@with_transaction
def test_21_pending_creation_rejection_test():
    """
    Tests that we can reject a pending object creation. Also tests
    that the right privileges are needed.
    Uses the pending creation from test_19.
    """
    # we call test_19 since we approved the last pending change on test_20
    test_19_pending_creation_test() 
    old_credit_count = len(john.credits)
    old_creation_count = Credit.get_pending_creations().count()
    pending_credit = Credit.get_pending_creations()[-1]
    
    set_user(None)
    try:
        pending_credit.reject()
        assert False, 'Anonymous users shouldn\'t be able to reject'
    except PermissionError, e:
        pass
    assert Credit.selectBy(personID=john.id).count() == old_credit_count
    assert Credit.get_pending_creations().count() == old_creation_count
    
    set_user(user)
    try:
        pending_credit.reject()
        assert False, 'Users shouldn\'t be able to reject'
    except PermissionError, e:
        pass
    assert Credit.selectBy(personID=john.id).count() == old_credit_count
    assert Credit.get_pending_creations().count() == old_creation_count
    
    set_user(admin1)
    try:
        pending_credit.reject()
    except PermissionError, e:
        assert False, 'Authorized users should be able to reject'
    assert Credit.selectBy(personID=john.id).count() == old_credit_count, \
        'Object was written'
    assert Credit.get_pending_creations().count() == old_creation_count - 1, \
        'Pending creation still there'

@with_transaction
def test_22_failed_create():
    """
    Tests that a failed creation doesn'\t leave a orphan state
    """
    set_user(admin1)
    select = ObjectStateTrace.selectBy(model_name='UnicodePerson')
    old_ost_count = select.count()
    
    UnicodePerson(name='12345678')
    assert select.count() == old_ost_count + 1, (old_ost_count, select.count())
    
    try:
        UnicodePerson(name='12345678')
        assert False, 'This should have failed, name should be unique'
    except AssertionError:
        raise
    except:
        # this should work under any kind of failure
        pass
    assert select.count() == old_ost_count + 1, \
            'The creation failures shouldn\'t write states.'

@with_transaction
def test_23_modify_after_creation():
    """
    Pending modfications after a pending creations were being identified as
    creations.
    """
    set_user(user)
    
    count = Credit.get_pending_creations().count()
    
    assert Credit.sqlmeta._creating is False
    
    try:
        Credit(amount=123332, person=john)
        assert False
    except PendingCreation, e:
        pass
    
    assert Credit.get_pending_creations().count() == count + 1
    assert Credit.sqlmeta._creating is False
    
    try:
        Credit.get(1).amount += 1000
    except PendingCreation, e:
        assert False, 'Pending creation while modifying'
    except PendingChange, e:
        pass
    
    assert Credit.sqlmeta._creating is False
    assert Credit.get_pending_creations().count() == count + 1, \
        'Creation created while modifying'

@with_transaction
def test_24_pending_change_with_set():
    """
    Test doing a pending modification with .set()
    """
    set_user(user)
    
    credit = Credit.get(1)
    old_amount = credit.amount
    old_pending_count = credit.get_pending_changes().count()
    old_mod_count = credit.get_modification_history().count()
    
    try:
        credit.set(amount=(credit.amount + 1000))
        assert False, 'This modification should be pending'
    except PendingChange, e:
        pass
    
    assert old_amount == credit.amount
    assert old_mod_count == credit.get_modification_history().count()
    
    pending_changes = credit.get_pending_changes()
    assert e.args[1] == pending_changes[-1]
    assert old_pending_count + 1 == pending_changes.count()
    assert pending_changes[-1]['amount'].old_value == old_amount
    assert pending_changes[-1]['amount'].new_value == old_amount + 1000

@with_transaction
def test_25_ost_comment():
    """
    Tests setting a comment on a OST.
    """
    set_user(user)
    
    credit = Credit.get(1)
    try:
        credit.amount += 1000
        assert False
    except PendingChange, e:
        pass
    
    ost = e.args[1]
    ost.comment = 'Pepe!'
    
    assert ost.comment == 'Pepe!'
    assert ost._states['comment'] == 'Pepe!'
    assert credit.get_pending_changes()[-1]._states['comment'] == 'Pepe!'

@with_transaction
def test_26_avoid_pendings_on_null_changes():
    """
    Tests that .set's or .__setattr__ don't raise a PendingChange if there
    are no changes made on the database.
    """
    
    set_user(user)
    
    credit = Credit.get(1)
    old_pending_count = credit.get_pending_changes().count()
    old_mod_count = credit.get_modification_history().count()
    
    try:
        credit.amount = credit.amount
    except PendingChange, e:
        assert False, 'Fired a PendingChange when no changes were made'
    assert old_pending_count == credit.get_pending_changes().count()
    assert old_mod_count == credit.get_modification_history().count()
    
    try:
        credit.set(amount=credit.amount)
    except PendingChange, e:
        assert False, 'Fired a PendingChange when no changes were made'
    assert old_pending_count == credit.get_pending_changes().count()
    assert old_mod_count == credit.get_modification_history().count()

@with_transaction
def test_27_approve_reject_comments():
    """
    Tests that comments are added to approves and rejects
    """
    
    test_03_pending_write()
    pending_changes = john.credits[0].get_pending_changes()
    set_user(admin1)
    pending_changes[-1].approve('Test Comment!')
    
    ost = john.credits[0].get_modification_history()[-1]
    assert ost.approves[0].comment == 'Test Comment!'
    
    test_03_pending_write()
    pending_changes = john.credits[0].get_pending_changes()
    set_user(admin1)
    pending_changes[-1].reject('Test Comment!')
    
    ost = john.credits[0].get_history()[-1]
    assert ost.rejects[0].comment == 'Test Comment!'

@with_transaction
def test_28_rollback_all():
    """
    Tests that a rollback also affects OST tables
    """
    old_age = john.age
    old_ost_count = ObjectStateTrace.select().count()
    old_data_count = TraceData.select().count()
    old_states_count = ObjectState.select().count()
    
    john.age += 1
    hub.rollback()
    john.sync()
    
    assert old_age == john.age
    assert old_ost_count == ObjectStateTrace.select().count()
    assert old_data_count == TraceData.select().count()
    assert old_states_count == ObjectState.select().count()


@with_transaction
def test_29_skip_ost():
    """
    Tests that setting cherrypy.request.skip_ost makes OST to ignore creations
    and modifications (as well as authorizations).
    """
    
    cherrypy.request.skip_ost = True
    
    old_age = john.age
    old_ost_count = ObjectStateTrace.select().count()
    old_data_count = TraceData.select().count()
    old_states_count = ObjectState.select().count()
    
    john.age += 1
    phone = Telephone(number='12345', person=john)
    
    assert old_age + 1 == john.age
    assert old_ost_count == ObjectStateTrace.select().count()
    assert old_data_count == TraceData.select().count()
    assert old_states_count == ObjectState.select().count()
    assert phone.get_history().count() == 0
    
    delattr(cherrypy.request, 'skip_ost')


@with_transaction
def test_30_set_and_fkey_bug():
    """
    """
    
    phone = Telephone(number='12345', person=john)
    
    count = phone.get_history().count()
    
    phone.set(person=jane)
    
    assert count + 1 == phone.get_history().count()

def test_31_race_condition_1():
    """
    This race condition happens if two approves are done by 
    two different users at the same time on an state that needs one 
    vote.
    
    If both threads start the transaction at the same time and 
    there is no locking two things can ocurr.
        1. A deadlock (no delays on either thread).
        2. Two creations, the last one would reassign the state to it,
           the first one would be left stateless (one delayed).
    
    The delay has to be introduced after both threads started the 
    transactions at the same time.
    
    Fixed in [2194].
    """
    
    @with_transaction
    def test(sleep_increment):
        test_19_pending_creation_test()
        
        old_count = Credit.select().count()
        
        pending_credit = Credit.get_pending_creations()[-1]
        
        threads = []
        threads.append(AuthThread(state_id=pending_credit.id, sleep=0.1,
                                  user=admin1, action='approve'))
        threads.append(AuthThread(state_id=pending_credit.id,
                                  sleep=0.1 + sleep_increment,
                                  user=admin2, action='approve'))
        
        for i in threads:
            i.start()
        
        for i in threads:
            i.join()
        
        for i in threads:
            assert i.finished_ok
        
        assert_equals(Credit.select(forUpdate=True).count(), old_count + 1)
    
    # Deadlock most of the times, other times two creations.
    test(sleep_increment=0)
    
    # Two creations.
    test(sleep_increment=0.1)

def test_31_race_condition_2():
    """
    This race condition happens if two approves are done by 
    two different users at the same time on an state that needs 
    two votes.
    
    If both threads start the transaction at the same time and 
    there is no locking two things can ocurr.
        1. A deadlock (no delays on either thread).
        2. No creations, both threads think the amount of votes 
           needed were not achieved (one delayed).
    
    The delay has to be introduced after both threads started the 
    transactions at the same time.
    
    Fixed in [2194].
    """
    
    def test(sleep_increment):
        state_id = make_pending_loan()
        real_test(sleep_increment, state_id)
    
    @with_transaction
    def make_pending_loan():
        set_user(user)
        
        try:
            Loan(amount=1000, person=john)
        except PendingCreation, e:
            state = e[1]
        else:
            assert False, 'Should have been pending'
        
        set_user(admin1)
        state.approve()
        
        return state.id
    
    @with_transaction
    def real_test(sleep_increment, state_id):
        old_count = Loan.select().count()
        
        threads = []
        threads.append(AuthThread(state_id=state_id, sleep=0.1,
                                  user=admin2, action='approve'))
        threads.append(AuthThread(state_id=state_id,
                                  sleep=0.1 + sleep_increment,
                                  user=admin3, action='approve'))
        
        for i in threads:
            i.start()
        
        for i in threads:
            i.join()
        
        for i in threads:
            assert i.finished_ok
        
        assert_equals(Loan.select(forUpdate=True).count(), old_count + 1)
    
    # Deadlock most of the times, other times no creations.
    test(sleep_increment=0)
    
    # No creations.
    test(sleep_increment=0.1)

@with_transaction
def test_32_double_state_on_overriden_setter():
    f = FriendShip.get(friendship.id)
    
    p1 = f.person_1
    p2 = f.person_2
    old_count = f.get_history().count()
    
    
    print
    print 'p1', p1
    print 'p2', p2
    print
    f.set(person_1ID=f.person_2ID, person_2ID=f.person_1ID)
    
    for i in f.get_history():
        print i.id, i.model_name, i.data
    
    assert_equals(f.get_history().count(), old_count + 1)
    assert_equals(p1, f.person_2)
    assert_equals(p2, f.person_1)


class AuthThread(threading.Thread):
    def __init__(self, state_id, sleep, user, action):
        super(AuthThread, self).__init__()
        self.state_id = state_id
        self.sleep = sleep
        self.finished_ok = False
        self.user = user
        
        assert action in ['approve', 'reject']
        self.action = action
    
    def log(self, *args):
        print time.time(), '\t', self.getName(), '\t',
        for i in args:
            print i,
        print
    
    @with_transaction
    def run(self):
        
        class dummy_request:
            class _session:
                session_storage = True
                session_data = dict()
                to_be_loaded = False
        
        cherrypy.serving.request = dummy_request
        
        set_user(self.user)
        time.sleep(self.sleep)
        
        cherrypy.request._OST_locking_selects = True
        self.log('GETTING STATE')
        state = ObjectStateTrace.get(self.state_id)
        self.log('STATE', state.id)
        
        if state.pending:
            if self.action == 'approve':
                state.approve(self.getName())
            else:
                state.reject(self.getName())
        
        self.finished_ok = True
        self.log('FINISHED')



# FIXME agregar un testeo de que alguien sin escritura pendiente pero con 
# escritura inmediata, pueda escribir (se corrigio un bug donde el no tener
# escritura pendiente hacia que se corte la modificacion

# FIXME agregar un test que cambie una fecha de nula a algo
# actualmente la fecha nueva se guardaria con la hora en el state
# al no tener para comparar no sabe que es date y no datetime.

# FIXME agregar un testeo del controller OST (corroborar permisos/accesos)

# FIXME testear user_mapper y user_model

# FIXME testear skip_ost_auth

