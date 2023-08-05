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

__all__ = ['ObjectStateTrace', 'TraceData', 'RejectVote', 'ApproveVote']

class UserValidator(Validator):
    def to_python(self, value, state):
        model = identity.soprovider.user_class
        return value and model.get(value) or None
    
    def from_python(self, value, state):
        return int(value and value.id or None)


class CommentMixin:
    def _set_comment(self, comment):
        self._states['comment'] = comment
    
    def _get_comment(self):
        return self._states.get('comment')
    comment = property(fget=_get_comment, fset=_set_comment)


class ObjectStateTrace(SQLObject, CommentMixin):
    class sqlmeta:
        table = 'ost_main'
    
    time = DateTimeCol(default=datetime.now)
    instance_id = IntCol()
    model_name = StringCol(length=50)
    user = IntCol(notNone=False, validator=UserValidator())
    pending = BoolCol(default=False)
    rejected = BoolCol(default=False)
    
    _index = index.DatabaseIndex(model_name, instance_id, time)
    
    data = MultipleJoin('TraceData', joinColumn='ost_id')
    
    def __getitem__(self, name):
        try:
            return TraceData.selectBy(ost=self, name=name)[0]
        except IndexError:
            raise KeyError
    
    def get_class(self):
        return classregistry.findClass(self.model_name)
    
    def get_object(self):
        "Returns the object being traced"
        return self.get_class().get(self.instance_id)
    
    rejects = MultipleJoin('RejectVote', joinColumn='state_id')
    approves = MultipleJoin('ApproveVote', joinColumn='state_id')
    
    def _check_auth(self):
        "Checks if the current state can be approved/rejected by the user."
        schema = self.get_class()._get_auth_schema(extra=self)
        if not schema:
            return
        if self.instance_id:
            if not schema.can_authorize_modification():
                raise PermissionError('User cannot approve/reject pending '
                                      'changes')
        else:
            if not schema.can_authorize_modification():
                raise PermissionError('User cannot approve/reject creations')
        
        if self.pending is False or self.rejected is True:
            raise PermissionError('This change has already been ' \
                                  'approved/rejected')
        user = identity.current.user
        if user in [i.user for i in self.rejects] or \
           user in [i.user for i in self.approves]:
            raise PermissionError('User ID %i already approved/rejected this '
                                  'change'  % user.id)
    
    def approve(self, comment=None):
        self._check_auth()
        vote = ApproveVote(state=self, user=identity.current.user)
        vote.comment = comment
        schema = self.get_class()._get_auth_schema(extra=self)
        if len(self.approves) >= schema.min_approves_needed:
            if self.instance_id:
                # if we are approving a modification, we fetch the instance
                # and write the changes
                obj = self.get_object()
                for data in self.data:
                    obj._orig_setattr(data.name, data.new_value)
                # NOTE: N updates vs single update (setattr vs set)
                # We can't use ._orig_set here because because SQLObject
                # will fire the decorated setattr from .set when a column
                # has a user defined setter/getter and we will end up with
                # extra writes, which means having extra modifications
                # traced.
                # I don't think that making the class lazy for this update
                # would be thread-safe, so we will have to do 1 update per
                # field atm.
            else:
                kw = dict()
                for data in self.data:
                    kw[data.name] = data.new_value
                obj = self.get_class()(from_ost_pending=self, **kw)
            self.pending = False
    
    def reject(self, comment=None):
        self._check_auth()
        vote = RejectVote(state=self, user=identity.current.user)
        vote.comment = comment
        schema = self.get_class()._get_auth_schema(extra=self)
        if len(self.rejects) >= schema.min_rejects_needed:
            self.rejected = True
    
    def can_authorize(self):
        schema = self.get_class()._get_auth_schema(extra=self)
        if self.instance_id:
            if schema.can_authorize_modification():
                return True
        else:
            if schema.can_authorize_creation():
                return True
        return False

ObjectStateTrace.sqlmeta.columns['user'].validator.validators.pop(0)

class TraceData(SQLObject):
    class sqlmeta:
        table = 'ost_trace_data'
    ost = ForeignKey('ObjectStateTrace', cascade=True)
    name = StringCol(length=100)
    old_value = BLOBCol(length=2**24-1, varchar=False, notNone=False)
    new_value = BLOBCol(length=2**24-1, varchar=False, notNone=False)
    
    _index = index.DatabaseIndex(ost, name, unique=True)
    
    def _get_old_value(self):
        return pickle.loads(self._SO_get_old_value().decode('base64'))
    
    def _set_old_value(self, value):
        self._SO_set_old_value(pickle.dumps(value).encode('base64'))
    
    def _get_new_value(self):
        return pickle.loads(self._SO_get_new_value().decode('base64'))
    
    def _set_new_value(self, value):
        self._SO_set_new_value(pickle.dumps(value).encode('base64'))


class TraceDataWrapper(object):
    def __init__(self, ost):
        self.ost = ost
    
    def __getitem__(self, name):
        try:
            return TraceData.selectBy(ost=self.ost, name=name)[0]
        except IndexError:
            raise KeyError


class RejectVote(SQLObject, CommentMixin):
    class sqlmeta:
        table = 'ost_rejects'
    state = ForeignKey('ObjectStateTrace', cascade=True)
    user = IntCol(validator=UserValidator())
    time = DateTimeCol(default=datetime.now)
    _index = index.DatabaseIndex(state, user, unique=True)
RejectVote.sqlmeta.columns['user'].validator.validators.pop(0)


class ApproveVote(SQLObject, CommentMixin):
    class sqlmeta:
        table = 'ost_approves'
    state = ForeignKey('ObjectStateTrace', cascade=True)
    user = IntCol(validator=UserValidator())
    time = DateTimeCol(default=datetime.now)
    _index = index.DatabaseIndex(state, user, unique=True)
ApproveVote.sqlmeta.columns['user'].validator.validators.pop(0)

