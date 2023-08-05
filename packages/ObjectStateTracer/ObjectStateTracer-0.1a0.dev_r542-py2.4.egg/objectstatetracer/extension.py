import logging

import cherrypy

from turbogears import config

from decorator import decorator

from sqlobject import *

from datetime import datetime, date

from array import array

import cPickle as pickle

from turbogears.database import PackageHub
hub = PackageHub('objectstatetracer.dburi')
__connection__ = hub

log = logging.getLogger('objectstatetracer')

orig_getattr = None
orig_set = None
classes = [] # this isnt thread safe, only safe to modify at startup
ObjectStateTrace = None
locked = False

def init_class():
    global ObjectStateTrace
    try:
        classregistry.findClass('ObjectStateTrace')
    except KeyError:
        class ObjectStateTrace(SQLObject):
            class sqlmeta:
                table = 'tg_ost'
            time = DateTimeCol(default=datetime.now)
            instance_id = IntCol()
            model_name = StringCol(length=255)
            column_name = StringCol(length=255)
            old_value = BLOBCol(length=2**24-1, varchar=False)
            new_value = BLOBCol(length=2**24-1, varchar=False)
            _index = index.DatabaseIndex(model_name, instance_id, time)
            
            def _get_old_value(self):
                class_ = classregistry.findClass(self.model_name)
                if not class_:
                    raise 'Cannot get history info from a non declared class'
                return to_python(class_, self.column_name, 
                                 self._SO_get_old_value(),
                                 state=self._SO_validatorState)
            
            def _get_new_value(self):
                class_ = classregistry.findClass(self.model_name)
                if not class_:
                    raise 'Cannot get history info from a non declared class'
                return to_python(class_, self.column_name, 
                                 self._SO_get_new_value(),
                                 state=self._SO_validatorState)
        ObjectStateTrace.createTable(ifNotExists=True)

def start_extension():
    global orig_setattr, orig_set, locked
    
    locked = True
    
    if not config.get("objectstatetracer.on", False):
        return
    
    log.info('OST starting')
    
    init_class()
    orig_set = SQLObject.set
    SQLObject.set = audit_set(orig_set)
    
    orig_setattr = SQLObject.__setattr__
    SQLObject.__setattr__ = audit_setattr(orig_setattr)
    SQLObject.get_modification_history = get_modification_history
    
    log.info('OST intialised')

def stop_extension():
    if not config.get("objectstatetracer.on", False):
        return
    SQLObject.set = orig_set
    SQLObject.__setattr__ = orig_setattr
    del SQLObject.get_modification_history

def save_trace(obj, col, old_value, new_value, time=None):
    if not time:
        time = datetime.now()
    if not obj.sqlmeta.columns.has_key(col):
        ## foreign key columns, when set directly like:
        ## model.person = Person(name='John')
        ## will trigger a model.personID set too.
        ## we don't need to do it here.
        return
    ObjectStateTrace(instance_id=obj.id, time=time,
                     model_name=obj.__class__.__name__,
                     column_name=col,
                     old_value=from_python(obj, col, old_value),
                     new_value=from_python(obj, col, new_value))

def process_values(obj, col, old_value):
    new_value = getattr(obj, col)
    if isinstance(old_value, SQLObject):
        old_value = old_value.id
    if isinstance(new_value, SQLObject):
        new_value = new_value.id
    if isinstance(old_value, date) and isinstance(new_value, datetime):
        new_value = new_value.date()
    return (old_value, new_value)

def save_if_changed(obj, col, old_value, time=None):
    old_value, new_value = process_values(obj, col, old_value)
    if old_value != new_value:
        save_trace(obj, col, old_value, new_value, time=time)
        return True

def audit_setattr(func):
    def wrapped(obj, col, new_value):
        is_column = hasattr(obj, '_SO_val_' + col)
        old_value = is_column and getattr(obj, col) or None
        ret = func(obj, col, new_value)
        if obj.__class__ in classes and is_column:
            save_if_changed(obj, col, old_value)
        else:
            pass
        return ret
    return wrapped

def audit_set(func):
    def wrapped(obj, **kw):
        modified = dict()
        if kw and obj.__class__ in classes and not obj.sqlmeta._creating:
            for k,v in kw.iteritems():
                if k == 'id':
                    pass
                modified[k] = getattr(obj, k) # we save the old values
        ret = func(obj, **kw)
        now = datetime.now()
        for col, old_value in modified.iteritems():
            save_if_changed(obj, col, old_value, time=now)
        return ret
    return wrapped

def get_modification_history(self):
    return ObjectStateTrace.select(
                AND(ObjectStateTrace.q.instance_id == self.id,
                    ObjectStateTrace.q.model_name == self.__class__.__name__))

def register_class(class_):
    if not locked:
        classes.append(class_)
    else:
        raise 'Registering a class is only possible at startup'

def from_python(obj, col_name, value, state=None):
    return pickle.dumps(value)

def to_python(obj, col_name, value, state=None):
    return pickle.loads(value)

