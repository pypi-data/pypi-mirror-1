from tw.api import Widget, JSLink, CSSLink, js_function
from tw.forms import TableForm
from js import prototype_js
from formencode import Schema

ajax_form_js = JSLink(modname=__name__, filename='static/javascript/ajax_form.js', javascript=[])
json_js = JSLink(modname=__name__,      filename='static/javascript/json2.js',     javascript=[])

class FilteringSchema(Schema):
    filter_extra_fields = True
    allow_extra_fields = True

class ActiveForm(TableForm):
    template = "genshi:toscawidgets.widgets.prototype.templates.table_form"

    javascript = [prototype_js, ajax_form_js, json_js]
    include_dynamic_js_calls = True

    _params = ['on_success', 'on_failure', 'clear_on_success']
    params = _params
    manager = js_function('new AjaxFormManager')

    validator = FilteringSchema

    def update_params(self, d):
        super(ActiveForm, self).update_params(d)
        
        if not getattr(d, 'id', None):
            raise KeyError('ActiveForm widgets require an id')
        
        options = dict()
        for i in self._params:
            options[i] = d[i]
        
        self.add_call(self.manager(d.id, options))
