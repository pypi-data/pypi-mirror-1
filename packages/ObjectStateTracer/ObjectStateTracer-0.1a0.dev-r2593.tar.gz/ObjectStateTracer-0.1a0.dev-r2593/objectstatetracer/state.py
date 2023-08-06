import cPickle as pickle

from sqlobject import *

from registry import *

from model import ObjectStateTrace, EngineCheckerMixin

from turbogears.database import PackageHub

hub = PackageHub('objectstatetracer.dburi')
__connection__ = hub

__all__ = ['ObjectState', 'get_states_wrapper']

class ObjectState(EngineCheckerMixin, SQLObject):
    """
    Class to implement a kind of vertical table over existing objects
    """
    class sqlmeta:
        table = 'ost_states'
    
    instance_id = IntCol()
    model_name = StringCol(length=50)
    name = StringCol(length=100)
    value = BLOBCol(length=2**24-1, varchar=False)
    
    _index = index.DatabaseIndex(model_name, instance_id, name, unique=True)
    
    def _get_value(self):
        return pickle.loads(self._SO_get_value().decode('base64'))
    
    def _set_value(self, value):
        self._SO_set_value(pickle.dumps(value).encode('base64'))
    
    def _audited_SO_set(self, func, **kw):
        kw['extra'] = kw
        return super(ObjectState, self)._audited_SO_set(func, **kw)
    
    def _audited_SO_setattr(self, func, col, new_value):
        extra = dict(model_name=self.model_name)
        return super(ObjectState, self).\
                _audited_SO_setattr(func, col, new_value, extra=extra)
    
    def _audited_SO_finishCreate(self, id=None):
        extra = dict(model_name=self.model_name)
        return super(ObjectState, self).\
                _audited_SO_finishCreate(id, extra=extra)
     
    @classmethod
    def _get_auth_schema(cls, extra=None):
        if isinstance(extra, ObjectStateTrace):
            state = extra.get_object()
            if state.instance_id:
                extra = dict(model_name=state.model_name)
        class_ = classregistry.findClass(extra['model_name'])
        return getattr(class_, '_auth_schema', None)
    
    @classmethod
    def _audit(cls, model_name):
        if classregistry.findClass(model_name) in classes:
            return True
        return False


class OSWrapper(dict):
    def __init__(self, model):
        self.model = model
    
    def _get_state(self, name):
        q = ObjectState.q
        sel = ObjectState.selectBy(model_name=self.model.__class__.__name__,
                                   instance_id=self.model.id, name=name)
        try:
            return sel[0]
        except IndexError:
            raise KeyError
    
    def __getitem__(self, item):
        state = self._get_state(item)
        return state.value
    
    def __setitem__(self, item, value):
        try:
            state = self._get_state(item)
            state.value = value
        except KeyError:
            ObjectState(instance_id=self.model.id, name=item, value=value,
                        model_name=self.model.__class__.__name__)
    
    def __delitem__(self, item):
        item = self._get_state(item)
        item.destroySelf()
    
    def get(self, name, default=None):
        try:
            return self._get_state(name).value
        except KeyError:
            return default
    
    def keys(self):
        states = ObjectState.selectBy(instance_id=self.model.id,
                                      model_name=self.model.__class__.__name__)
        return [i.name for i in states]
    
    def has_key(self, name):
        try:
            self._get_state(name)
            return True
        except KeyError:
            return False
    
    def approve(self, name):
        return self._get_state(name).approve()
    
    def reject(self, name):
        return self._get_state(name).reject()
    
    def get_history(self, name):
        return self._get_state(name).get_history()
    
    def get_modification_history(self, name):
        return self._get_state(name).get_modification_history()
    
    def get_pending_changes(self, name):
        return self._get_state(name).get_pending_changes()
    
    def get_rejected_changes(self, name):
        return self._get_state(name).get_rejected_changes()

def get_states_wrapper(self):
    return OSWrapper(self)
