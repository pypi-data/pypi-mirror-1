import pkg_resources

from turbogears.widgets import Widget, WidgetDescription, DataGrid, Label, \
                               CSSLink, JSLink, register_static_directory
from turbogears import expose, database, url, identity
from turbojson import jsonify
from sqlobject import *
from elementtree import ElementTree as ET

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

@generic()
def display_widgets_for(model):
    "Returns a list of widgets for a model"
    pass

class HistoryPanel(DataGrid):
    css = [CSSLink(css_dir, 'history_panel.css')] + DataGrid.css
    
    def _get_widget(self, name):
        return self.display_widgets[name]
    
    def _get_field_name(self, state):
        return self._get_widget(state.column_name).label
    
    def _get_old_value(self, state):
        return self._get_widget(state.column_name).display(state.old_value)
    
    def _get_new_value(self, state):
        return self._get_widget(state.column_name).display(state.new_value)
    
    def _get_user(self, state):
        return unicode(state.user)
    
    def _get_status(self, state):
        status_div = ET.Element('div')
        status_div.set('class', 'history_panel')
        
        status = ET.SubElement(status_div, 'div')
        status.set('class', 'status')
        
        if not state.pending and not state.rejected:
            status.text = 'Written'
        elif state.pending and not state.rejected:
            status.text = 'Pending'
            
            model = classregistry.findClass(state.model_name)
            schema = model.get(state.instance_id)._get_auth_schema()
            if schema.can_authorize_modification():
                approve_url = url('/objectstatetracer/approve_modification',
                                  state_id=state.id)
                approve = ET.SubElement(status, 'span')
                approve.set('class', 'approve_button')
                approve_link = ET.SubElement(approve, 'a', href=approve_url)
                approve_link.text = 'Approve'
                
                reject_url = url('/objectstatetracer/reject_modification',
                                 state_id=state.id)
                reject = ET.SubElement(status, 'span')
                reject.set('class', 'reject_button')
                reject_link = ET.SubElement(reject, 'a', href=reject_url)
                reject_link.text = 'Reject'
            
        elif state.pending and state.rejected:
            status.text = 'Rejected'
        
        if state.approves:
            approves = ET.SubElement(status_div, 'div')
            approves.set('class', 'approves')
            approves.text = 'Approved By:'
            for approve in state.approves:
                span = ET.SubElement(approves, 'div')
                span.set('class', 'approver')
                span.text = u'%s at %s' % (unicode(approve.user), approve.time)
        
        if state.rejects:
            rejects = ET.SubElement(status_div, 'div')
            rejects.set('class', 'rejects')
            rejects.text = 'Rejected By:'
            for reject in state.rejects:
                span = ET.SubElement(rejects, 'div')
                span.set('class', 'rejecter')
                span.text = u'%s at %s' % (unicode(reject.user), reject.time)
        
        return status_div
    
    def __init__(self, display_widgets, model, mappings=dict(), *args, **kw):
        fields = [DataGrid.Column(name='time', title='Modification Time'),
                  DataGrid.Column(name='user', getter=self._get_user,
                                  title='User'),
                  DataGrid.Column(name='column_name',
                                  getter=self._get_field_name, title='Field'),
                  DataGrid.Column(name='old_value', getter=self._get_old_value,
                                  title='Old Value'), 
                  DataGrid.Column(name='new_value', getter=self._get_new_value,
                                  title='New Value'),
                  DataGrid.Column(name='status', getter=self._get_status,
                                  title='Status')]
        kw['fields'] = fields
        
        super(HistoryPanel, self).__init__(*args, **kw)
        
        self.model = model
        self.display_widgets = dict()
        self.mappings = mappings
        for widget in display_widgets:
            if mappings.has_key(widget.name):
                print 'via mappings'
            elif self.model.sqlmeta.columns.has_key(widget.name):
                name = widget.name
            elif self.model.sqlmeta.columns.has_key(widget.name + 'ID'):
                name = widget.name + 'ID'
            else:
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
        object = d['value']
        super(HistoryPanel, self).update_params(d)
        d['value'] = object.get_history().reversed()


class AuthPanel(HistoryPanel):
    def update_params(self, d):
        object = d['value']
        super(AuthPanel, self).update_params(d)
        d['value'] = object.get_pending_changes().reversed()
        schema = object._get_auth_schema()
        if schema and not schema.can_authorize_modification():
            d['value'].filter(OST.q.user == identity.current.user.id)


class OSTMenu(Widget):
    "OST Menu Panel"
    
    js = [JSLink(js_dir, 'ost_menu.js')] + Window.javascript
    css = [CSSLink(css_dir, 'ost_menu.css')] + Window.css
    template = 'objectstatetracer.templates.ost_menu'
    
    def update_params(self, d):
        super(OSTMenu, self).update_params(d)
        show = False
        options = dict()
        
        d['options'] = jsonify.encode(options)
        d['pending_changes'] = d['value'].get_pending_changes()
        
        model_name = d['value'].__class__.__name__
        instance_id = d['value'].id
        
        if d['pending_changes'].count() > 0:
            show = True
            d['pending_changes_url'] = url('/objectstatetracer/modifications',
                                           model_name=model_name,
                                           instance_id=instance_id,
                                           history='pending')
        schema = d['value']._get_auth_schema()
        if schema and schema.can_authorize_modification():
            show = True
            d['mod_history_url'] = url('/objectstatetracer/modifications',
                                       model_name=model_name,
                                       instance_id=instance_id)
        
        d['show'] = show
