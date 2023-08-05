import exceptions

from model import ObjectStateTrace

from registry import *

from state import *

from sqlobject import classregistry

__all__ = ['SOOSTBase']

class SOOSTBase:
    """
    This class will be added as a base to SQLObject classes to add new methods
    and properties.
    """
    
    _states = property(get_states_wrapper)
    
    def _get_auth_schema(self):
        if isinstance(self, ObjectState):
            class_ = classregistry.findClass(self.model_name)
            return getattr(class_, '_auth_schema', None)
        return getattr(self, '_auth_schema', None)
    
    @property
    def _auditable(self):
        "Determines if a class should be audited or not"
        class_ = self.__class__
        if isinstance(self, ObjectState):
            class_ = classregistry.findClass(self.model_name)
        if class_ in classes:
            return True
        return False
    
    #FIXME: cambiar el nombre de esto
    def _check_permissions(self):
        schema = self._get_auth_schema()
        if schema:
            if not schema.can_modify_any():
                raise exceptions.PermissionError(
                        'User doesn\'t have permission to write on %s' \
                            % self.__class__.__name__)
            elif schema.can_modify_pending() and not schema.can_modify():
                raise exceptions.PendingChange(
                        'User needs authorization to write on %s' \
                            % self.__class__.__name__)
    
    def _audited_SO_set(self, func, **kw):
        self._check_permissions()
        return func(self, **kw)

    def _audited_SO_setattr(self, func, col, new_value):
        self._check_permissions()
        return func(self, col, new_value)
    
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

