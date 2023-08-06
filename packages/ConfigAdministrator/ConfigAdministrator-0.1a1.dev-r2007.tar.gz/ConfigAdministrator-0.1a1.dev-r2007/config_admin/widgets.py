import pkg_resources

from turbogears import validators 

from turbogears.widgets import CSSLink, JSLink, Widget, WidgetDescription, \
                               register_static_directory, TableForm, \
                               TextField, WidgetsList, HiddenField, \
                               InputWidget, SingleSelectField

js_dir = pkg_resources.resource_filename("config_admin",
                                         "static/javascript")
register_static_directory("config_admin", js_dir)

from controllers import configuration_panels

from model import ConfigOption

class ConfigPanel(object):
    def retrieve_javascript(self):
        return self.form.retrieve_javascript()
    
    def retrieve_css(self):
        return self.form.retrieve_css()
    
    def __init__(self, name, options, predicate=None, validator=None, **kw):
        super(ConfigPanel, self).__init__(**kw)
        
        self.predicate = predicate
        self.name = name
        self.options = options
        if configuration_panels.has_key(name):
            raise 'A ConfigPanel with that name arealdy exists'
        configuration_panels[name] = self
        
        form_fields = [HiddenField('panel', default=self.name)]
        for option in options:
            if isinstance(option, InputWidget):
                form_fields.append(option)
            elif hasattr(option, 'widget'):
                form_fields.append(option.widget(option.name, 
                                                 **option.widget_params))
        
        self.form = TableForm(fields=form_fields, action='/config_admin/',
                              validator=validator)
    
    def get(self, option):
        try:
            cp = ConfigOption.selectBy(name=option, panel=self.name)[0]
        except IndexError:
            return None
        return cp.value
    
    def display(self, **kw):
        values = dict()
        for co in ConfigOption.selectBy(panel=self.name):
            values[co.name] = co.value
        return self.form.display(value=values, **kw)

class SOConfigOption(Widget):
    template = """
        <div xmlns:py="http://purl.org/kid/ns#">
            pum!
        </div>
    """
    
    def __init__(self, model, condition=None, select=None, items=1, 
                 nullable=False, validator=validators.Int, **kw):
        super(SOConfigOption, self).__init__(**kw)
        self.widget_params = kw
        if items == 1:
            self.widget = SingleSelectField
            def get_options():
                if nullable:
                    list = [(None, '')]
                else:
                    list = []
                for i in model.select():
                    list.append((i.id, unicode(i)))
                return list
            self.widget_params['options'] = get_options
            self.widget_params['validator'] = validator
        else:
            self.widget = TextField
