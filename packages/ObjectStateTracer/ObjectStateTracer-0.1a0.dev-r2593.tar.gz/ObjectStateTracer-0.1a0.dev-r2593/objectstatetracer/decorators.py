import exceptions

from datetime import datetime, date

from sqlobject import SQLObject, AND, OR, SOForeignKey

from cherrypy import request

from model import *

from registry import *

from util import normalize_values

from state import ObjectState

__all__ = ['audit_setattr', 'audit_set', 'audit_create']

def audit_setattr(func):
    def wrapped(obj, col, new_value):
        is_column = hasattr(obj, '_SO_val_' + col)
        old_value = is_column and getattr(obj, col)
        
        def audit():
            if isinstance(obj, ObjectState):
                return obj._audit(model_name=obj.model_name)
            return obj._audit()
            
        if not is_column or getattr(request, 'skip_ost', False) or not audit():
            return func(obj, col, new_value)        
        
        ret = None
        pending = False
        try:
            obj._audited_SO_setattr(func, col, new_value)
        except exceptions.PendingChange, e:
             pending = True
        ost = obj._save_trace({col: (old_value, new_value)}, pending=pending)
        
        if ost and pending:
            raise exceptions.PendingChange(e.args[0], ost)
    return wrapped

def is_foreign_key(obj, col):
    if not obj.sqlmeta.columns.has_key(col) and \
       obj.sqlmeta.columns.has_key(col + 'ID') and \
       isinstance(obj.sqlmeta.columns[col + 'ID'], SOForeignKey):
        return True
    return False

def audit_set(func):
    def wrapped(obj, **kw):
        modified = dict()
        if kw and obj.__class__ in classes:
            for k,v in kw.iteritems():
                if k == 'id':
                    continue
                
                if is_foreign_key(obj, k):
                    # If it's a ForeignKey column we only want to set the ID
                    # properties (person vs personID) to prevent SO from doing
                    # a setattr with them, or else we will end writing the
                    # change on multiple OST's.
                    if obj.sqlmeta._creating:
                        old_value = None
                        new_value = kw.pop(k)
                    else:
                        old_value = getattr(obj, k + 'ID')
                        new_value = kw.pop(k)
                    old_value, new_value = normalize_values(old_value,
                                                            new_value)
                    modified[k + 'ID'] = old_value
                    kw[k + 'ID'] = new_value
                    continue
                
                if obj.sqlmeta._creating:
                    modified[k] = None # old_value on creation states is none
                else:
                    modified[k] = getattr(obj, k) # we save the old values
        
        if isinstance(obj, ObjectState):
            audit = obj._audit(model_name=kw['model_name'])
        else:
            audit = obj._audit()
        
        # If the class is not audited or audits are skipped globally
        # we just return the value.
        if not audit or getattr(request, 'skip_ost', False):
            return func(obj, **kw)
        
        data = dict()
        pending = False
        creation = False
        try:
            obj._audited_SO_set(func, **kw)
        except exceptions.PendingChange, e:
            pending = True
        except exceptions.PendingCreation, e:
            pending = True
            creation = True
        for col, old_value in modified.iteritems():
            data[col] = (old_value, kw[col])
        ost = obj._save_trace(data, pending=pending)
        
        if ost and pending and not creation:
            raise exceptions.PendingChange(e.args[0], ost)
    return wrapped

def audit_create(func):
    def wrapped(obj, id=None):
        if isinstance(obj, ObjectState):
            audit = obj._audit(model_name=obj.model_name)
        else:
            audit = obj._audit()
        
        if not audit or getattr(request, 'skip_ost', False):
            return func(obj, id)
        
        try:
            obj._audited_SO_finishCreate(id)
        except exceptions.PendingCreation, e:
            # del instance value (leaving the class one which is false)
            # this prevents us from leaving the model on perma creation status
            del obj.sqlmeta._creating
            raise exceptions.PendingCreation(e.args[0], obj._creating_ost)
    return wrapped

