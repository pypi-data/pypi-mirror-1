import exceptions

import sys

import logging

import traceback

from turbogears.controllers import expose, Controller, flash, redirect
from turbogears.decorator import simple_decorator
from turbogears.database import rollback_all
from turbogears import url, identity

from sqlobject import classregistry, AND, OR

from widgets import HistoryPanel, ost_list, display_widgets_for, OSTTraceData, \
                    images_dir, get_details_panel

from model import ObjectStateTrace as OST, hub

from cherrypy import request, HTTPRedirect

from registry import auth_schemas

from scriptaculous.widgets import scriptaculous

from div_dialogs.widgets import Window

from localization import gettext_ost

log = logging.getLogger('objectstatetracer.controllers')

window = Window()

@simple_decorator
def report_error(func, *args, **kw):
    try:
        return func(*args, **kw)
    except HTTPRedirect, e:
        raise
    except:
        log.error('Error while calling %s. Auth Args: %s, %s' \
                    %  (func.__name__, args[1:], kw))
        print
        print traceback.format_exc()
        print
        rollback_all()
    flash('An error ocurred while processing the approve/reject')
    raise redirect(request.headers.get('Referer', '/'))

class HistoryController(Controller):
    @expose(template='objectstatetracer.templates.state_details')
    def state_detail(self, state_id=None):
        state = OST.get(state_id)
        model = state.get_class()
        panel = get_details_panel(model)
        schema = model._get_auth_schema()
        
        # only users authorizing or owning the state can see it
        if state.user != identity.current.user and \
           not schema.can_authorize_modification() and \
           not schema.can_authorize_creation():
            raise identity.IdentityFailure([])
        
        approve_url = url('/objectstatetracer/auth', action='approve',
                          state_id=state.id)
        reject_url = url('/objectstatetracer/auth', action='reject',
                          state_id=state.id)
        
        return dict(state=state, model=model, object=object, panel=panel,
                    images_dir=images_dir, approve_url=approve_url,
                    reject_url=reject_url, window=window,
                    G_=gettext_ost)
    
    @expose(template='objectstatetracer.templates.history')
    def history(self, model_name, instance_id=None, show_pending_only=False):
        "Shows a datagrid with the events from an object or model"
        model = classregistry.findClass(model_name)
        panel = HistoryPanel(model=model)
        schema = model._get_auth_schema()
        
        if instance_id:
            object = model.get(instance_id)
            if show_pending_only:
                states = object.get_pending_changes()
            else:
                states = object.get_history()
        else:
            if show_pending_only:
                states = model.get_pending_creations()
            else:
                states = model.get_creations()
        
        # If the user can't authorize only show their related states
        if not schema.can_authorize_modification() and \
           not schema.can_authorize_creation():
            if identity.current.user:
                states = states.filter(OST.q.user == identity.current.user.id)
            else:
                staets = states.filter(OST.q.user == None)
        return dict(states=states, panel=panel,
                    G_=gettext_ost)
        
    @expose(template='objectstatetracer.templates.pendings')
    def pending_states(self, model_name=None, modifications_only=False,
                       creations_only=False, authorizable=False):
        "Shows a datagrid with pending states."
        states = OST.selectBy(pending=True, rejected=False)
        
        if model_name:
            states = states.filter(OST.q.model_name == model_name)
        
        if modifications_only:
            states = states.filter(OST.q.instance_id != None)
        
        if creations_only:
            states = states.filter(OST.q.instance_id == None)
        
        if authorizable: # shows authorizable pendings
            # This is expensive, but as far as I know it's not doable in
            # other way with the current predicate system.
            pendings = states
            states = []
            user = identity.current.user
            for state in pendings:
                if user in [i.user for i in state.approves + state.rejects]:
                    # Don't show states already voted.
                    continue
                if state.can_authorize():
                    states.append(state)
        else:
            # shows current user pendings
            states = states.filter(OST.q.user == identity.current.user.id)
        
        return dict(panel=ost_list, pendings=states, extra_js=scriptaculous,
                    G_=gettext_ost)
    
    @expose(format='json')
    def notifier_feeder(self):
        if identity.current.anonymous:
            return dict(pending=False)
        pendings = OST.selectBy(pending=True, rejected=False)
        user = identity.current.user
        for state in pendings:
            if user in [i.user for i in state.approves + state.rejects]:
                # Don't count states already voted.
                continue
            if state.can_authorize():   
                return dict(pending=True)
        return dict(pending=False)
    
    @expose()
    @report_error
    def auth(self, action, state_id, comment=None):
        url = request.headers.get('Referer', '/')
        request._OST_locking_selects = True
        state = OST.get(state_id, forUpdate=True)
        
        if not state.can_authorize() or action not in ['approve', 'reject']:
            flash(_('Cannot authorize this object'))
            raise redirect(url)
        if not state.pending:
            flash(_('This object is not pending'))
            raise redirect(url)
        
        try:
            if action == 'approve':
                state.approve(comment)
                flash(_('Approved'))
            else:
                state.reject(comment)
                flash(_('Rejected'))
        except exceptions.PermissionError, e:
            flash(e.args[0])
            rollback_all()
        
        raise redirect(url)

