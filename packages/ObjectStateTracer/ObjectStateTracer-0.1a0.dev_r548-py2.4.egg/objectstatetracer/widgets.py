from turbogears.widgets import Widget, WidgetDescription, DataGrid, Label
from turbogears import expose, database
from sqlobject import *

file_fields = None
try:
    from file_fields.widgets import FileField, ImageField, ImagePreview
    file_fields = True
except ImportError:
    pass

from dispatch import generic
from dispatch.interfaces import NoApplicableMethods

@generic()
def _get_display_widget(widget):
    """This function returns a read-only version of the passed widget"""
    pass

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

class HistoryPanel(DataGrid):
    def _get_widget(self, name):
        return self.display_widgets[name]
    
    def _get_field_name(self, state):
        return self._get_widget(state.column_name).label
    
    def _get_old_value(self, state):
        return self._get_widget(state.column_name).display(state.old_value)
    
    def _get_new_value(self, state):
        return self._get_widget(state.column_name).display(state.new_value)
    
    def __init__(self, display_widgets, model, mappings=dict(), *args, **kw):
        fields = [DataGrid.Column(name='time', title='Modification Time'),
                  DataGrid.Column(name='column_name',
                                  getter=self._get_field_name, title='Field'),
                  DataGrid.Column(name='old_value', getter=self._get_old_value,
                                  title='Old Value'), 
                  DataGrid.Column(name='new_value', getter=self._get_new_value,
                                  title='New Value')]
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
        super(HistoryPanel, self).update_params(d)
        #history = d['value'].get_modification_history()
        
        # by_time = []
        # current_time = None
        # states = []
        # for state in history:
            # if current_time != state.time:
                # if current_time:
                    # by_time.append((current_time, states))
                # current_time = state.time
                # states = []
            # states.append(state)
        # d['history_by_time'] = by_time
        
        # FIXME: la simplifico hasta terminar bien todo
        #d['history_by_time'] = history.reversed()
        
        d['value'] = d['value'].get_modification_history().reversed()

# demo not working due to DB config problems
'''
class HistoryPanelDescription(object): 
    for_widget = HistoryPanel()
    template = """
    <div xmlns:py="http://purl.org/kid/ns#">
        ${for_widget.display(object)}
    </div>
    """
    show_separately = True
    
    def __init__(self):
        class TestPerson(SQLObject):
            name = StringCol(length=50)
            age = IntCol()
        TestPerson.createTable()
        self.object = TestPerson(name='John', age=30)
    
    def update_params(self, d):
        super(HistoryPanelDescription, self).update_params(d)
        d['object'] = self.object
        print self.object
    
    @expose()
    def index(self):
        pass
'''

