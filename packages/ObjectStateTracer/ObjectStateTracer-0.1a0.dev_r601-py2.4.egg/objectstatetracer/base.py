import exceptions

from model import ObjectStateTrace, TraceData

from registry import *

from state import *

from sqlobject import classregistry, SQLObject

from datetime import date, datetime

from turbogears import config, identity

from util import normalize_values

from exceptions import *

__all__ = ['SOOSTBase']

class SOOSTBase:
    """
    This class will be added as a base to SQLObject classes to add new methods
    and properties.
    """
    
    _states = property(get_states_wrapper)
    
    @classmethod
    def _get_auth_schema(cls, extra=None):
        return getattr(cls, '_auth_schema', None)
    
    @classmethod
    def _audit(cls):
        "Determines if a class should be audited or not"
        if cls in classes:
            return True
        return False
    
    def _check_permissions(self, extra=None):
        schema = self._get_auth_schema(extra=extra)
        if not schema:
            return
        if self.sqlmeta._creating:
            if not schema.can_create_any():
                raise exceptions.PermissionError(
                        'User doesn\'t have permission to create a %s' \
                            % self.__class__.__name__)
            elif schema.can_create_pending() and not schema.can_create():
                raise exceptions.PendingCreation(
                        'User needs authorization to create a %s' \
                            % self.__class__.__name__)
        else:
            if not schema.can_modify_any():
                raise exceptions.PermissionError(
                        'User doesn\'t have permission to modify %s' \
                            % self.__class__.__name__)
            elif schema.can_modify_pending() and not schema.can_modify():
                raise exceptions.PendingChange(
                        'User needs authorization to modify %s' \
                            % self.__class__.__name__)
    
    def _audited_SO_set(self, func, extra=None, **kw):
        if kw.has_key('from_ost_pending'):
            state = self._from_ost_pending = kw.pop('from_ost_pending')
            schema = self._get_auth_schema(extra=extra)
            if not isinstance(state, ObjectStateTrace) or \
               not isinstance(self, state.get_class()) or \
               not schema.can_authorize_creation():
                raise PermissionError('The user did something weird. Had ' \
                                      'permission to approve/reject an object '
                                      'creation but he didn\'t have those '
                                      'permissions when we checked before '
                                      'writing.')
        else:
            self._check_permissions(extra=extra)
        return func(self, **kw)

    def _audited_SO_setattr(self, func, col, new_value, extra=None):
        self._check_permissions(extra=extra)
        return func(self, col, new_value)
    
    def _audited_SO_finishCreate(self, id=None, extra=None):
        if not hasattr(self, '_from_ost_pending'):
            self._check_permissions(extra=extra)
        try:
            id = self._orig_SO_finishCreate(id)
        except:
            # if creation fails for any reason we have to drop the state
            # object
            if hasattr(self, '_creating_ost'):
                self._creating_ost.destroySelf()
            raise
        if hasattr(self, '_creating_ost'):
            self._creating_ost.instance_id = self.id
            if hasattr(self, '_from_ost_pending'):
                # if this creation comes from a pending state we have to
                # delete the extra state created from the authorization write
                self._creating_ost.destroySelf()
                # and reference the pending one to the new object
                self._from_ost_pending.instance_id = self.id
        return id
    
    def get_history(self):
        """
        Returns all the events on the object, modifications, pending changes and
        rejected changes.
        """
        return ObjectStateTrace.selectBy(instance_id=self.id,
                                         model_name=self.__class__.__name__)
    
    def get_modification_history(self):
        "Returns the changes made to the object."
        return ObjectStateTrace.selectBy(instance_id=self.id,
                                         model_name=self.__class__.__name__,
                                         pending=False, rejected=False)
    
    def get_pending_changes(self):
        "Returns the pending changes on the object."
        return ObjectStateTrace.selectBy(instance_id=self.id,
                                         model_name=self.__class__.__name__,
                                         pending=True, rejected=False)
    
    def get_rejected_changes(self):
        "Returns the rejected changes on the object."
        return ObjectStateTrace.selectBy(instance_id=self.id,
                                         model_name=self.__class__.__name__,
                                         pending=True, rejected=True)
    
    @classmethod
    def get_pending_creations(cls):
        "Returns the pending creations on the object."
        return ObjectStateTrace.selectBy(instance_id=None,
                                         model_name=cls.__name__,
                                         pending=True, rejected=False)
    
    def _save_trace(self, data, pending=False):
        # 1st verify if there are changes, we skip non updates
        trace_data = dict()
        for col, (old_value, new_value) in data.iteritems():
            if not self.sqlmeta.columns.has_key(col):
                # foreign key columns, when set directly like:
                # model.person = Person(name='John')
                # will trigger a model.personID set too.
                # we don't need to do it here.
                continue
            old_value, new_value = normalize_values(old_value, new_value)
            if old_value == new_value:
                continue
            trace_data[col] = (old_value, new_value)
        
        # abort if there's no trace data to be saved
        if not trace_data:
            return
        
        user = None
        if config.get('identity.on', False):
            user = identity.current.user
        
        instance_id = None
        if not self.sqlmeta._creating:
            instance_id = self.id
        
        ost = ObjectStateTrace(instance_id=instance_id, time=datetime.now(), 
                               user=user, model_name=self.__class__.__name__,
                               pending=pending)
        
        if self.sqlmeta._creating:
            # If it's a new object we store the state on sqlmeta
            # so the instance_id can be set later (or not if it's a pending
            # creation).
            self._creating_ost = ost
        
        for col, (old_value, new_value) in trace_data.iteritems():
            TraceData(ost=ost, name=col, old_value=old_value,
                      new_value=new_value)
        
        return ost








