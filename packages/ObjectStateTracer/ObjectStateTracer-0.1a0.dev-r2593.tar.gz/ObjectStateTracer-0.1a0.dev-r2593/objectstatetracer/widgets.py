import pkg_resources
import logging

import warnings
try:
    import cElementTree as ET
except ImportError:
    from elementtree import ElementTree as ET

from turbogears.widgets import Widget, WidgetDescription, DataGrid, Label, \
                               CSSLink, JSLink, register_static_directory
from turbogears import expose, database, url, identity
from turbojson import jsonify
from sqlobject import *
from inspect import isclass

file_fields = None
try:
    from file_fields.widgets import FileField, ImageField, ImagePreview
    file_fields = True
except ImportError:
    pass

from dispatch import generic
from dispatch.interfaces import NoApplicableMethods

from div_dialogs.widgets import Window

from model import ObjectStateTrace as OST

from localization import gettext_ost

log = logging.getLogger('objectstatetracer.widgets')

js_dir = pkg_resources.resource_filename('objectstatetracer',
                                         'static/javascript')
register_static_directory('objectstatetracer.js', js_dir)
js_dir = 'objectstatetracer.js'

css_dir = pkg_resources.resource_filename('objectstatetracer',
                                          'static/css')
register_static_directory('objectstatetracer.css', css_dir)
css_dir = 'objectstatetracer.css'

images_dir = pkg_resources.resource_filename('objectstatetracer',
                                             'static/images')
register_static_directory('objectstatetracer.images', images_dir)
images_dir = 'objectstatetracer.images'

__all__ = ['HistoryPanel', 'AuthPanel']

_ = gettext_ost

@generic()
def _get_display_widget(widget):
    """This function returns a read-only version of the passed widget"""
    pass

#FIXME: hacer un entry point para esto
if file_fields:
    # @_get_readonly_widget.when('isinstance(widget, FileField)')
    # def _get_readonly_widget(widget):
        # return Label()
    
    @_get_display_widget.when('isinstance(widget, ImageField)')
    def _get_display_widget(widget):
        return ImagePreview(widget.name, label=widget.label,
                            thumb_dimensions=widget.validator.thumb_dimensions,
                            base64=widget.validator.base64)

def get_display_widget(widget):
    try:
        return _get_display_widget(widget)
    except NoApplicableMethods:
        return Label(label=widget.label)

def get_details_panel(model):
    try:
        return details_panel_for(model)
    except NoApplicableMethods:
        return OSTTraceData(model=model)

@generic()
def display_widgets_for(model):
    "Returns a list of widgets for a model"
    pass

@generic()
def details_panel_for(model):
    "Returns a widget that will display the detailed information from a OST"
    pass

@generic()
def extra_information_for(state):
    """
    This function should return extra information to be displayed on the 
    extra column on the pending states panel.
    """
    pass

class OSTTraceData(DataGrid):
    "DataGrid that shows the modifactions contained in a single OST"
    def _get_widget(self, name):
        return self.display_widgets[name]
    
    def _get_field_name(self, state):
        return self._get_widget(state.name).label
    
    def _get_old_value(self, state):
        return self._get_widget(state.name).display(state.old_value)
    
    def _get_new_value(self, state):
        return self._get_widget(state.name).display(state.new_value)
    
    def __init__(self, model, *args, **kw):
        fields = [DataGrid.Column(name='column_name',
                                  getter=self._get_field_name,
                                  title=_('Field')),
                  DataGrid.Column(name='old_value', getter=self._get_old_value,
                                  title=_('Old Value')), 
                  DataGrid.Column(name='new_value', getter=self._get_new_value,
                                  title=_('New Value'))]
        kw['fields'] = fields
        
        super(OSTTraceData, self).__init__(*args, **kw)
        
        self.model = model
        display_widgets = display_widgets_for(model)
        
        self.display_widgets = dict()
        for widget in display_widgets:
            if self.model.sqlmeta.columns.has_key(widget.name):
                name = widget.name
            elif self.model.sqlmeta.columns.has_key(widget.name + 'ID'):
                name = widget.name + 'ID'
            else:
                log.debug('Skipping widget %s=%s, couldn\'t find a column with '
                          'that name.' % (widget.name, type(widget)))
                continue
            widget = get_display_widget(widget)
            self.display_widgets[name] = widget
            for js in widget.javascript:
                if js not in self.javascript:
                    self.javascript.append(js)
            for css in widget.css:
                if css not in self.css:
                    self.css.append(css)
    
    def update_params(self, d):
        super(OSTTraceData, self).update_params(d)
        states = d['value'][:]
        for state in states:
            try:
                self._get_widget(state.name)
            except KeyError:
                d['value'].remove(state)


class HistoryPanel(DataGrid):
    "Displays the OST's from a given object"
    css = [CSSLink(css_dir, 'history_panel.css')] + DataGrid.css + Window.css
    javascript = Window.javascript + [JSLink(js_dir, 'history_panel.js')] 
    
    def _get_user(self, state):
        return unicode(state.user)
    
    def _get_changes(self, state):
        return self.trace_data.display(state.data)
    
    def _get_status(self, state):
        status_div = ET.Element('div')
        status_div.set('class', 'history_panel')
        
        if state.comment:
            comment = ET.SubElement(status_div, 'div')
            comment.set('class', 'comment')
            comment.text = state.comment
        
        status = ET.SubElement(status_div, 'div')
        status.set('class', 'status')
        
        if not state.pending and not state.rejected:
            status.text = 'Written'
        elif state.pending and not state.rejected:
            status.text = 'Pending'
            
            model = classregistry.findClass(state.model_name)
            schema = model._get_auth_schema()
            if schema.can_authorize_modification():
                approve_url = url('/objectstatetracer/auth', state_id=state.id,
                                  action='approve')
                reject_url = url('/objectstatetracer/auth', state_id=state.id,
                                  action='reject')
                approve_url = 'javascript:approve("%s");' % approve_url
                reject_url = 'javascript:reject("%s");' % reject_url
                
                approve = ET.SubElement(status, 'span')
                approve.set('class', 'approve_button')
                approve_link = ET.SubElement(approve, 'a', href=approve_url)
                approve_link.text = _('Approve')
                
                reject = ET.SubElement(status, 'span')
                reject.set('class', 'reject_button')
                reject_link = ET.SubElement(reject, 'a', href=reject_url)
                reject_link.text = _('Reject')
            
        elif state.pending and state.rejected:
            status.text = _('Rejected')
        
        if state.approves:
            approves = ET.SubElement(status_div, 'div')
            approves.set('class', 'approves')
            approves.text = _('Approved By:')
            for approve in state.approves:
                span = ET.SubElement(approves, 'div')
                span.set('class', 'approver')
                span.text = u'%s at %s' % (unicode(approve.user), approve.time)
                if approve.comment:
                    comment = ET.SubElement(span, 'div')
                    comment.text = approve.comment
        
        if state.rejects:
            rejects = ET.SubElement(status_div, 'div')
            rejects.set('class', 'rejects')
            rejects.text = _('Rejected By:')
            for reject in state.rejects:
                span = ET.SubElement(rejects, 'div')
                span.set('class', 'rejecter')
                span.text = u'%s at %s' % (unicode(reject.user), reject.time)
                if reject.comment:
                    comment = ET.SubElement(span, 'div')
                    comment.text = reject.comment
        
        return status_div
    
    def __init__(self, model, *args, **kw):
        fields = [DataGrid.Column(name='id', title=_('Trace ID')),
                  DataGrid.Column(name='time', title=_('Time')),
                  DataGrid.Column(name='user', getter=self._get_user,
                                  title=_('User')),
                  DataGrid.Column(name='changes', getter=self._get_changes,
                                  title=_('Changes')),
                  DataGrid.Column(name='status', getter=self._get_status,
                                  title=_('Status'))]
        kw['fields'] = fields
        
        super(HistoryPanel, self).__init__(*args, **kw)
        
        self.trace_data = OSTTraceData(model=model)
        
        for js in self.trace_data.javascript:
                if js not in self.javascript:
                    self.javascript.append(js)
        for css in self.trace_data.css:
            if css not in self.css:
                self.css.append(css)


class OSTList(DataGrid):
    """
    Displays a list of OST's listing their:
        id, type (creation|modification), class, instance_id
    """
    
    def _get_user(self, state):
        return unicode(state.user)
    
    def _get_type(self, state):
        if state.instance_id:
            return _('Modification')
        return _('Creation')
    
    def _get_actions(self, state):
        link_url = url('/objectstatetracer/state_detail', state_id=state.id)
        link_url = 'javascript:open_state_detail("%s");' % link_url
        link = ET.Element('a', href=link_url)
        link.text = _('Details')
        return link
    
    def _get_extra_information(self, state):
        try:
            return extra_information_for(state)
        except NoApplicableMethods:
            return None
    
    def __init__(self, *args, **kw):
        fields = [DataGrid.Column(name='id', title=_('Trace ID')),
                  DataGrid.Column(name='time', title=_('Time')),
                  DataGrid.Column(name='user', getter=self._get_user,
                                  title=_('User')),
                  DataGrid.Column(name='type', getter=self._get_type,
                                  title=_('Type')),
                  DataGrid.Column(name='model_name', title=_('Object Type')),
                  DataGrid.Column(name='instance_id', title=_('Object ID')),
                  DataGrid.Column(name='extra_information',
                                  getter=self._get_extra_information,
                                  title=_('Extra')),
                  DataGrid.Column(name='actions', getter=self._get_actions,
                                  title=_('Actions'))]
        kw['fields'] = fields
        super(OSTList, self).__init__(*args, **kw)
ost_list = OSTList()


class OSTMenu(Widget):
    "OST Menu Panel"
    
    javascript = [JSLink(js_dir, 'ost_menu.js')] + Window.javascript
    css = [CSSLink(css_dir, 'ost_menu.css')] + Window.css
    template = 'objectstatetracer.templates.ost_menu'
    
    def update_params(self, d):
        super(OSTMenu, self).update_params(d)
        options = dict()
        
        d['options'] = jsonify.encode(options)
        
        if isclass(d['value']) and issubclass(d['value'], SQLObject):
            model_name = d['value'].__name__
            
            d['pending_creations'] = d['value'].get_pending_creations()
            d['pending_changes'] = d['value'].get_model_pending_changes()
            
            schema = d['value']._get_auth_schema()
            if schema.can_authorize_modification():
                authorizable = True
            else:
                authorizable = ''
                user_id = identity.current.user and \
                          identity.current.user.id or None
                d['pending_changes'] = \
                    d['pending_changes'].filter(OST.q.user == user_id)
                d['pending_creations'] = \
                    d['pending_creations'].filter(OST.q.user == user_id)
            
            d['creation_history_url'] = url('/objectstatetracer/history',
                                            model_name=model_name)
            
            if d['pending_creations'].count() > 0:
                d['pending_creations_url'] = url('/objectstatetracer/history',
                                                 model_name=model_name,
                                                 show_pending_only=True)
            if d['pending_changes'].count() > 0:
                d['pending_changes_url'] = \
                    url('/objectstatetracer/pending_states',
                        model_name=model_name, modifications_only=True,
                        authorizable=authorizable)
        else:
            model_name = d['value'].__class__.__name__
            instance_id = d['value'].id
            
            d['pending_changes'] = d['value'].get_pending_changes()
            if d['pending_changes'].count() > 0:
                d['pending_changes_url'] = url('/objectstatetracer/history',
                                               model_name=model_name,
                                               instance_id=instance_id,
                                               show_pending_only=True)
            
            d['mod_history_url'] = url('/objectstatetracer/history',
                                       model_name=model_name,
                                       instance_id=instance_id)


class OSTNotifier(Widget):
    """
    A widget that when included in a page will only display if the current
    user can authorize a pending creation/modification. It will also check
    every 30 seconds (changeable) if there are new pending states.
    """
    
    javascript = Window.javascript + [JSLink(js_dir, 'ost_notifier.js')]
    css = [CSSLink(css_dir, 'ost_notifier.css')] + Window.css
    template = 'objectstatetracer.templates.ost_notifier'
    
    params = ['id', 'check_interval', 'pendings_url', 'notifier_url']
    id = 'ost_notifier'
    check_interval = 30 # 30 seconds default
    notifier_url = '/objectstatetracer/notifier_feeder'
    pendings_url = '/objectstatetracer/pending_states?authorizable=1'
    
    def update_params(self, d):
        super(OSTNotifier, self).update_params(d)
        options = dict()
        for i in ['notifier_url', 'pendings_url', 'check_interval']:
            options[i] = d[i]
        d['options'] = jsonify.encode(options)
        d['G_'] = gettext_ost
ost_notifier = OSTNotifier()

