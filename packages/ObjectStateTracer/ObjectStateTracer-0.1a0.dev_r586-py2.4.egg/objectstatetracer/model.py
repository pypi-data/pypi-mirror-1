import cPickle as pickle

from sqlobject import *

from turbogears import identity
from turbogears.database import PackageHub

from datetime import datetime

from formencode.validators import Validator

from registry import *

from exceptions import *

hub = PackageHub('objectstatetracer.dburi')
__connection__ = hub

__all__ = ['ObjectStateTrace', 'RejectVote', 'ApproveVote']

class UserValidator(Validator):
    def to_python(self, value, state):
        model = identity.soprovider.user_class
        return value and model.get(value) or None
    
    def from_python(self, value, state):
        return int(value and value.id or None)


class ObjectStateTrace(SQLObject):
    class sqlmeta:
        table = 'ost_modifications'
    
    time = DateTimeCol(default=datetime.now)
    instance_id = IntCol()
    model_name = StringCol(length=50)
    column_name = StringCol(length=100)
    old_value = BLOBCol(length=2**24-1, varchar=False)
    new_value = BLOBCol(length=2**24-1, varchar=False)
    user = IntCol(notNone=False, validator=UserValidator())
    
    _index = index.DatabaseIndex(model_name, instance_id, time)
    
    pending = BoolCol(default=False)
    rejected = BoolCol(default=False)
    
    def get_object(self):
        "Returns the object being traced"
        class_ = classregistry.findClass(self.model_name)
        return class_.get(self.instance_id)
    
    def _get_old_value(self):
        return pickle.loads(self._SO_get_old_value().decode('base64'))
    
    def _set_old_value(self, value):
        self._SO_set_old_value(pickle.dumps(value).encode('base64'))
    
    def _get_new_value(self):
        return pickle.loads(self._SO_get_new_value().decode('base64'))
    
    def _set_new_value(self, value):
        self._SO_set_new_value(pickle.dumps(value).encode('base64'))
    
    rejects = MultipleJoin('RejectVote', joinColumn='state_id')
    approves = MultipleJoin('ApproveVote', joinColumn='state_id')
    
    def approve(self):
        user = identity.current.user
        obj = self.get_object()
        schema = obj._get_auth_schema()
        if not schema.can_authorize_modification():
            raise PermissionError('User cannot approve pending changes')
        if self.pending is False or self.rejected is True:
            raise PermissionError('This change has already been ' \
                                  'approved/rejected')
        if user in [i.user for i in self.approves]:
            raise PermissionError('User ID %i already approved this change' \
                                    % user.id)
        ApproveVote(state=self, user=user)
        if len(self.approves) >= schema.min_approves_needed:
            obj._orig_setattr(self.column_name, self.new_value)
            self.pending = False
    
    def reject(self):
        user = identity.current.user
        obj = self.get_object()
        schema = obj._get_auth_schema()
        if not schema.can_authorize_modification():
            raise PermissionError('User cannot reject pending changes')
        if self.pending is False or self.rejected is True:
            raise PermissionError('This change has already been ' \
                                  'approved/rejected')
        if user in [i.user for i in self.rejects]:
            raise PermissionError('User ID %i already rejected this change' \
                                    % user.id)
        RejectVote(state=self, user=user)
        if len(self.rejects) >= schema.min_rejects_needed:
            self.rejected = True
ObjectStateTrace.sqlmeta.columns['user'].validator.validators.pop(0)


class RejectVote(SQLObject):
    class sqlmeta:
        table = 'ost_rejects'
    state = ForeignKey('ObjectStateTrace')
    user = IntCol(validator=UserValidator())
    time = DateTimeCol(default=datetime.now)
    _index = index.DatabaseIndex(state, user, unique=True)
RejectVote.sqlmeta.columns['user'].validator.validators.pop(0)


class ApproveVote(SQLObject):
    class sqlmeta:
        table = 'ost_approves'
    state = ForeignKey('ObjectStateTrace')
    user = IntCol(validator=UserValidator())
    time = DateTimeCol(default=datetime.now)
    _index = index.DatabaseIndex(state, user, unique=True)
ApproveVote.sqlmeta.columns['user'].validator.validators.pop(0)

