import exceptions

from datetime import datetime, date

from sqlobject import SQLObject, AND, OR

from turbogears import config, identity

from model import *

from registry import *

__all__ = ['audit_setattr', 'audit_set']

def audit_setattr(func):
    def wrapped(obj, col, new_value):
        is_column = hasattr(obj, '_SO_val_' + col)
        old_value = is_column and getattr(obj, col)
        
        if not is_column or not obj._auditable:
            return func(obj, col, new_value)
        
        ret = None
        try:
            ret = obj._audited_SO_setattr(func, col, new_value)
            _trace_if_changed(obj, col, old_value)
        except exceptions.PendingChange:
             _trace_if_changed(obj, col, old_value, new_value=new_value,
                               pending=True)
        return ret
    return wrapped

def audit_set(func):
    def wrapped(obj, **kw):
        modified = dict()
        if kw and obj.__class__ in classes and not obj.sqlmeta._creating:
            for k,v in kw.iteritems():
                if k != 'id':
                    if not obj.sqlmeta.columns.has_key(k) and \
                       obj.sqlmeta.columns.has_key(k + 'ID'):
                        modified[k] = getattr(obj, k + 'ID')
                    else:
                        modified[k] = getattr(obj, k) # we save the old values
        
        if obj.sqlmeta._creating or not obj._auditable:
            return func(obj, **kw)
        
        now = datetime.now()
        ret = None
        try:
            ret = obj._audited_SO_set(func, **kw)
            for col, old_value in modified.iteritems():
                _trace_if_changed(obj, col, old_value, time=now)
        except exceptions.PendingChange:
            for col, old_value in modified.iteritems():
                _trace_if_changed(obj, col, old_value, new_value=kw[col], 
                                  time=now, pending=True)
        return ret
    return wrapped

def _process_values(obj, col, old_value, **kw):
    if kw.has_key('new_value'):
        new_value = kw['new_value']
    else:
        new_value = getattr(obj, col)
    if isinstance(old_value, SQLObject):
        old_value = old_value.id
    if isinstance(new_value, SQLObject):
        new_value = new_value.id
    if isinstance(old_value, date) and isinstance(new_value, datetime):
        new_value = new_value.date()
    return (old_value, new_value)

def _trace_if_changed(obj, col, old_value, time=None, pending=False, **kw):
    old_value, new_value = _process_values(obj, col, old_value, **kw)
    if old_value != new_value:
        _save_trace(obj, col, old_value, new_value, time=time, pending=pending)
        return True

def _save_trace(obj, col, old_value, new_value, time=None, pending=False):
    if old_value == new_value:
        return
    if not time:
        time = datetime.now()
    if not obj.sqlmeta.columns.has_key(col):
        ## foreign key columns, when set directly like:
        ## model.person = Person(name='John')
        ## will trigger a model.personID set too.
        ## we don't need to do it here.
        return
    user = None
    if config.get('identity.on', False):
        user = identity.current.user
    ObjectStateTrace(instance_id=obj.id, time=time,
                     model_name=obj.__class__.__name__,
                     column_name=col, user=user, old_value=old_value,
                     new_value=new_value, pending=pending)

