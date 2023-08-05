import exceptions

import sys

import logging

from turbogears.controllers import expose, Controller, flash, redirect
from turbogears.decorator import simple_decorator
from turbogears.database import rollback_all
from turbogears import url, identity

from sqlobject import classregistry, AND, OR

from widgets import HistoryPanel, ost_list, display_widgets_for, OSTTraceData, \
                    images_dir

from model import ObjectStateTrace as OST, hub

from cherrypy import request, HTTPRedirect

from registry import auth_schemas

from scriptaculous.widgets import scriptaculous

from div_dialogs.widgets import Window

log = logging.getLogger('objectstatetracer.controllers')

window = Window()

@simple_decorator
def report_error(func, *args, **kw):
    try:
        return func(*args, **kw)
    except HTTPRedirect, e:
        raise
    except:
        log.error('Error while calling %s. Exception: %s. Args: %s, %s' % \
                   (func.__name__, sys.exc_info()[0], args[1:], kw))
        rollback_all()
    flash('An error ocurred while processing the approve/reject')
    raise redirect(request.headers.get('Referer', '/'))

class HistoryController(Controller):
    @expose(template='objectstatetracer.templates.state_details')
    def state_detail(self, state_id=None):
        state = OST.get(state_id)
        model = state.get_class()
        panel = OSTTraceData(model=model)
        
        # only users authorizing can see this
        if not state.can_authorize():
            raise identity.IdentityFailure([])
        
        approve_url = url('/objectstatetracer/auth', action='approve',
                          state_id=state.id)
        reject_url = url('/objectstatetracer/auth', action='reject',
                          state_id=state.id)
        
        
        return dict(state=state, model=model, object=object, panel=panel,
                    images_dir=images_dir, approve_url=approve_url,
                    reject_url=reject_url, window=window)
    
    @expose(template='objectstatetracer.templates.history')
    def history(self, model_name, instance_id=None, show_pending_only=False):
        "Shows a datagrid with all the events from an object"
        model = classregistry.findClass(model_name)
        panel = HistoryPanel(model=model)
        schema = model._get_auth_schema()
        object = model.get(instance_id)
        
        if show_pending_only:
            states = object.get_pending_changes()
        else:
            states = object.get_history()
        
        # Only users that can authorize modifications/creations can see 
        # the object's history.
        # Users owning the pending changes can see them too (only the pending).
        if not schema.can_authorize_modification() and \
           not schema.can_authorize_creation():
            # If the user can't authorize only show their related states
            if identity.current.user:
                states.filter(OST.q.user == identity.current.user.id)
            else:
                states.filter(OST.q.user == None)
            if not schema.can_modify_pending() or not show_pending_only:
                raise identity.IdentityFailure([])
        
        return dict(states=states, panel=panel)
    
    @expose(template='objectstatetracer.templates.pendings')
    def pending_states(self):
        "Shows a datagrid with all the pending states the user can authorize"
        pendings = []
        for state in OST.selectBy(pending=True, rejected=False):
            if state.can_authorize():
                pendings.append(state)
        return dict(panel=ost_list, pendings=pendings,
                    extra_js=scriptaculous)
    
    @expose(format='json')
    def notifier_feeder(self):
        if identity.current.anonymous:
            return dict(pending=False)
        pendings = OST.selectBy(pending=True, rejected=False)
        for state in pendings:
            if state.can_authorize():   
                return dict(pending=True)
        return dict(pending=False)
    
    @expose()
    @report_error
    def auth(self, action, state_id, comment=None):
        state = OST.get(state_id)
        if not state.can_authorize() or action not in ['approve', 'reject']:
            raise identity.IdentityFailure([])
        try:
            if action == 'approve':
                state.approve(comment)
                flash('Approved!')
            else:
                state.reject(comment)
                flash('Rejected!')
        except exceptions.PermissionError, e:
            flash(e.args[0])
        raise redirect(request.headers.get('Referer', '/'))

