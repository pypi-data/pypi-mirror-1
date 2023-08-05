import types

from turbogears import identity

__all__ = ['AuthSchema']

class AuthSchema(object):
    def __init__(self, modify, modify_pending, authorize_modification,
                 min_approves_needed=1,
                 min_rejects_needed=1, **kw):
        """
        Predicates are used this way:
        @param modify will determine if the user can modify or not.
        
        @param modify_pending will determine if the user can modify changes that
        need approval.
        
        @param authorize will determine can approve/reject pending changes.
    """
        self.modify = modify
        self.modify_pending = modify_pending
        self.authorize_modification = authorize_modification
        self.min_approves_needed = min_approves_needed
        self.min_rejects_needed = min_rejects_needed
        self.class_ = None
    
    def attach_class(self, class_):
        self.class_ = class_
        class_._auth_schema = self
    
    def can_modify_any(self, obj=None):
        return self.can_modify_pending(obj) or self.can_modify(obj) or \
               self.can_authorize_modification(obj)
    
    def can_modify(self, obj=None):
        if isinstance(self.modify, identity.Predicate):
            return self.modify.eval_with_object(identity.current)
        elif isinstance(self.modify, types.FunctionType):
            return self.modify(obj)
        raise TypeError(self.modify)
        
    def can_modify_pending(self, obj=None):
        if isinstance(self.modify_pending, identity.Predicate):
            return self.modify_pending.eval_with_object(identity.current)
        elif isinstance(self.modify_pending, types.FunctionType):
            return self.modify_pending(obj)
        raise TypeError(self.modify_pending)
    
    def can_authorize_modification(self, obj=None):
        if isinstance(self.authorize_modification, identity.Predicate):
            return self.authorize_modification.\
                    eval_with_object(identity.current)
        elif isinstance(self.authorize_modification, types.FunctionType):
            return self.authorize_modification(obj)
        raise TypeError(self.authorize_modification)

