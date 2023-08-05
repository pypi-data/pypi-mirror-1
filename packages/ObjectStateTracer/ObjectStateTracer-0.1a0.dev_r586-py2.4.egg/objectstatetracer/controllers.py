import exceptions

from turbogears.controllers import expose, Controller, flash, redirect
from turbogears.decorator import simple_decorator, weak_signature_decorator
from turbogears import url, identity

from sqlobject import classregistry

from widgets import HistoryPanel, AuthPanel, display_widgets_for

from model import ObjectStateTrace as OST

from cherrypy import request

@simple_decorator
def can_authorize_modifications(func, *args, **kw):
    model_name = OST.get(args[1]).model_name
    model = classregistry.findClass(model_name)
    if not model._auth_schema.can_authorize_modification():
        raise identity.IdentityFailure([])
    return func(*args, **kw)

class HistoryController(Controller):
    @expose(template='objectstatetracer.templates.history')
    def modifications(self, model_name, instance_id, history=None):
        model = classregistry.findClass(model_name)
        
        if not model._auth_schema.can_authorize_modification():
            if not (model._auth_schema.can_modify_pending() and
                    history == 'pending'):
                raise identity.IdentityFailure([])
        
        object = model.get(instance_id)
        widgets = display_widgets_for(model)
        if not history:
            panel = HistoryPanel(display_widgets=widgets, model=model)
        elif history == 'pending':
            panel = AuthPanel(display_widgets=widgets, model=model)
        return dict(object=object, panel=panel)
    
    @expose()
    @can_authorize_modifications
    def approve_modification(self, state_id):
        state = OST.get(state_id)
        try:
            state.approve()
            flash('Change Approved!')
        except exceptions.PermissionError, e:
            flash(e.args[0])
        raise redirect(request.headers.get('Referer', '/'))
    
    @expose()
    @can_authorize_modifications
    def reject_modification(self, state_id):
        state = OST.get(state_id)
        try:
            state.reject()
            flash('Change Rejected!')
        except exceptions.PermissionError, e:
            flash(e.args[0])
        raise redirect(request.headers.get('Referer', '/'))

