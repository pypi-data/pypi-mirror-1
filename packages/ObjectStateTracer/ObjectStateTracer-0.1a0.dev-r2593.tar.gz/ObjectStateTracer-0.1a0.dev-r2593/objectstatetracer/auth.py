import logging

import types

import cPickle

from turbogears import identity

from cache import request_cache

log = logging.getLogger('objectstatetracer.auth')

__all__ = ['AuthSchema']

# The cache is useful when the auth predicates do a lot of queries
# (like in my case). The cache is only PER REQUEST, so it's short lived
def cache_per_request(func):
    def wrapped(*args, **kw):
        cache = request_cache('auth')
        
        user = identity.current.user and identity.current.user.id or None
        
        try:
            key = (func, args[0], cPickle.dumps((args[1:], kw, user)))
        except:
            # if we can get a key, we can't cache the result
            log.info('Couldn\'t cache: %s, %s, %s.' % (args, kw, user))
            return func(*args, **kw)
        
        # I'm using the user for the cache too because the user may be changed
        # during the request
        try:
            output = cache[key]
        except KeyError:
            output = cache[key] = func(*args, **kw)
        
        return output
    return wrapped

class AuthSchema(object):
    def __init__(self, 
                 modify, modify_pending, authorize_modification,
                 create, create_pending, authorize_creation,
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
        
        self.create = create
        self.create_pending = create_pending
        self.authorize_creation = authorize_creation
        
        self._min_approves_needed = min_approves_needed
        self._min_rejects_needed = min_rejects_needed
        self.class_ = None
    
    def attach_class(self, class_):
        self.class_ = class_
        class_._auth_schema = self
    
    def min_rejects_needed(self, obj):
        if callable(self._min_rejects_needed):
            return self._min_rejects_needed(obj)
        return self._min_rejects_needed
    
    def min_approves_needed(self, obj):
        if callable(self._min_approves_needed):
            return self._min_approves_needed(obj)
        return self._min_approves_needed
    
    # modification
    @cache_per_request
    def can_modify_any(self, obj=None):
        return self.can_modify_pending(obj) or self.can_modify(obj) or \
               self.can_authorize_modification(obj)
    
    @cache_per_request
    def can_modify(self, obj=None):
        if isinstance(self.modify, identity.Predicate):
            return self.modify.eval_with_object(identity.current)
        elif isinstance(self.modify, types.FunctionType):
            return self.modify(obj)
        raise TypeError(self.modify)
    
    @cache_per_request
    def can_modify_pending(self, obj=None):
        if isinstance(self.modify_pending, identity.Predicate):
            return self.modify_pending.eval_with_object(identity.current)
        elif isinstance(self.modify_pending, types.FunctionType):
            return self.modify_pending(obj)
        raise TypeError(self.modify_pending)
    
    @cache_per_request
    def can_authorize_modification(self, obj=None):
        if isinstance(self.authorize_modification, identity.Predicate):
            return self.authorize_modification.\
                    eval_with_object(identity.current)
        elif isinstance(self.authorize_modification, types.FunctionType):
            return self.authorize_modification(obj)
        raise TypeError(self.authorize_modification)
    
    # creation
    @cache_per_request
    def can_create_any(self, obj=None):
        return self.can_create_pending(obj) or self.can_create(obj) or \
               self.can_authorize_creation(obj)
    
    @cache_per_request
    def can_create(self, obj=None):
        if isinstance(self.create, identity.Predicate):
            return self.create.eval_with_object(identity.current)
        elif isinstance(self.create, types.FunctionType):
            return self.create(obj)
        raise TypeError(self.create)
    
    @cache_per_request
    def can_create_pending(self, obj=None):
        if isinstance(self.create_pending, identity.Predicate):
            return self.create_pending.eval_with_object(identity.current)
        elif isinstance(self.create_pending, types.FunctionType):
            return self.create_pending(obj)
        raise TypeError(self.create_pending)
    
    @cache_per_request
    def can_authorize_creation(self, obj=None):
        if isinstance(self.authorize_creation, identity.Predicate):
            return self.authorize_creation.\
                    eval_with_object(identity.current)
        elif isinstance(self.authorize_creation, types.FunctionType):
            return self.authorize_creation(obj)
        raise TypeError(self.authorize_creation)
