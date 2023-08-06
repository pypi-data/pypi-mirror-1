import cPickle as pickle

from sqlobject import *

from turbogears import identity, config
from turbogears.database import PackageHub
from cherrypy import request

from datetime import datetime

from formencode.validators import Validator

from registry import *

from exceptions import *

from cache import request_cache

hub = PackageHub('objectstatetracer.dburi')
__connection__ = hub

__all__ = ['ObjectStateTrace', 'TraceData', 'RejectVote', 'ApproveVote']

def get_user_model():
    model_name = config.get('objectstatetracer.user_model')
    if model_name:
        return classregistry.findClass(model_name)
    return identity.soprovider.user_class

class UserValidator(Validator):
    def to_python(self, value, state):
        model = get_user_model()
        return value and model.get(value) or None
    
    def from_python(self, value, state):
        mapper = config.get('objectstatetracer.user_mapper')
        model = get_user_model()
        if mapper:
            cache = request_cache('user_validator')
            
            if cache.has_key(value):
                return cache[value]
            
            module = '.'.join(mapper.split('.')[:-1])
            mapper = mapper.split('.')[-1]
            module = __import__(module, {}, {}, [mapper])
            cache[value] = getattr(module, mapper)(value)
            return cache[value]
        
        if value and not isinstance(value, model):
            raise Exception('If you specify a user_model different to the '
                            'one the identity framework is using, you have to '
                            'specify a user_mapper to map IDs between them.')
        
        return value and value.id or None


class CommentMixin:
    def _set_comment(self, comment):
        self._states['comment'] = comment
    
    def _get_comment(self):
        return self._states.get('comment')
    comment = property(fget=_get_comment, fset=_set_comment)


class EngineCheckerMixin(object):
    '''
    This mixin will make sure that if the engine is MySQL the tables are 
    created as InnoDB (transactional) tables.
    '''
    
    @classmethod
    def createTable(cls, *args, **kw):
        if cls.tableExists(connection=cls._connection):
            return
        
        ret = super(EngineCheckerMixin, cls).createTable(*args, **kw)
        
        from sqlobject.mysql.mysqlconnection import MySQLConnection
        if isinstance(cls._connection._dbConnection, MySQLConnection):
            # if we just created the table, and the engine is MySQL
            # we have to be sure that the tables are InnoDB
            c = cls._connection
            c.query('ALTER TABLE `%s` ENGINE=InnoDB;' % cls.sqlmeta.table)
        
        return ret


class ObjectStateTrace(EngineCheckerMixin, SQLObject, CommentMixin):
    class sqlmeta:
        table = 'ost_main'
    
    time = DateTimeCol(default=datetime.now)
    instance_id = IntCol()
    model_name = StringCol(length=50)
    user = IntCol(notNone=False, validator=UserValidator())
    pending = BoolCol(default=False)
    rejected = BoolCol(default=False)
    
    _index = index.DatabaseIndex(model_name, instance_id, time)
    
    # Yes, this may look dumb, but we will only have very few pending = 1 rows
    # (if any) and those are the ones we are looking for on the auth panel.
    # This prevents a full table scan.
    _index_2 = index.DatabaseIndex(pending, rejected)
    
    data = MultipleJoin('TraceData', joinColumn='ost_id')
    
    def __getitem__(self, name):
        try:
            return TraceData.selectBy(ost=self, name=name)[0]
        except IndexError:
            raise KeyError
    
    @classmethod
    def get(cls, *args, **kw):
        forUpdate = kw.pop('forUpdate', False)
        if forUpdate or getattr(request, '_OST_locking_selects', False) and \
           kw.get('selectResults') is None:
            try:
                return cls.select(cls.q.id == args[0], forUpdate=True)[0]
            except IndexError:
                raise SQLObjectNotFound
        return super(ObjectStateTrace, cls).get(*args, **kw)
    
    def get_class(self):
        return classregistry.findClass(self.model_name)
    
    def get_object(self):
        "Returns the object being traced"
        return self.get_class().get(self.instance_id)
    
    @property
    def schema(self):
        return self.get_class()._get_auth_schema(extra=self)
    
    @property
    def min_rejects_needed(self):
        return self.schema.min_rejects_needed(self)
    
    @property
    def min_approves_needed(self):
        return self.schema.min_approves_needed(self)
    
    @property
    def rejects(self):
        forUpdate = False
        if getattr(request, '_OST_locking_selects', False):
            forUpdate = True
        return list(RejectVote.select(RejectVote.q.stateID == self.id,
                                       forUpdate=forUpdate))
    
    @property
    def approves(self):
        forUpdate = False
        if getattr(request, '_OST_locking_selects', False):
            forUpdate = True
        return list(ApproveVote.select(ApproveVote.q.stateID == self.id,
                                       forUpdate=forUpdate))
    
    def _check_auth(self):
        "Checks if the current state can be approved/rejected by the user."
        schema = self.get_class()._get_auth_schema(extra=self)
        if not schema:
            return
        if self.instance_id:
            if not schema.can_authorize_modification(self):
                raise PermissionError('User cannot approve/reject pending '
                                      'changes')
        else:
            if not schema.can_authorize_creation(self):
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
        if hasattr(self.get_class(), '_ost_approve'):
            self.get_class()._ost_approve(self)
        vote = ApproveVote(state=self, user=identity.current.user)
        vote.comment = comment
        if len(self.approves) >= self.min_approves_needed:
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
        if hasattr(self.get_class(), '_ost_reject'):
            self.get_class()._ost_reject(self)
        vote = RejectVote(state=self, user=identity.current.user)
        vote.comment = comment
        if len(self.rejects) >= self.min_rejects_needed:
            self.rejected = True
    
    def can_authorize(self):
        schema = self.get_class()._get_auth_schema(extra=self)
        if self.instance_id:
            if schema.can_authorize_modification(self):
                return True
        else:
            if schema.can_authorize_creation(self):
                return True
        return False

ObjectStateTrace.sqlmeta.columns['user'].validator.validators.pop(0)

class TraceData(EngineCheckerMixin, SQLObject):
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


class RejectVote(EngineCheckerMixin, SQLObject, CommentMixin):
    class sqlmeta:
        table = 'ost_rejects'
    state = ForeignKey('ObjectStateTrace', cascade=True)
    user = IntCol(validator=UserValidator())
    time = DateTimeCol(default=datetime.now)
    _index = index.DatabaseIndex(state, user, unique=True)
RejectVote.sqlmeta.columns['user'].validator.validators.pop(0)


class ApproveVote(EngineCheckerMixin, SQLObject, CommentMixin):
    class sqlmeta:
        table = 'ost_approves'
    state = ForeignKey('ObjectStateTrace', cascade=True)
    user = IntCol(validator=UserValidator())
    time = DateTimeCol(default=datetime.now)
    _index = index.DatabaseIndex(state, user, unique=True)
ApproveVote.sqlmeta.columns['user'].validator.validators.pop(0)

