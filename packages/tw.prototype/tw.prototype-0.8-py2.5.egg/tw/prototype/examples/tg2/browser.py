from tg import expose, flash, redirect, TGController
import pylons

from toscawidgets.widgets.forms.fields import *
from toscawidgets.widgets.prototype.activeform import ActiveForm
from twtools.frameworks.tg2.activeform import ActiveFormResponseHandler

from formencode.validators import Int, String

children = [TextField('non_empty_string', validator=String(not_empty=True)),
            TextField('integer', validator=Int()),
            ]
activeForm = ActiveForm(id='myActiveForm', action='submit', children=children, clear_on_success=True, on_success="console.log('hello!')")

class ActiveFormBrowser(TGController):

    @expose('toscawidgets.widgets.prototype.examples.tg2.templates.index')
    def form(self, **kw):
        pylons.c.w.widget = activeForm
        return dict()

    def submitSuccess(self, **kw):
        #this is where your database call goes
        print kw

    activeFormHandler = ActiveFormResponseHandler(activeForm, submitSuccess)
    submit            = activeFormHandler.ajax_submit

    def __call__(self, environ, start_response):
        """Invoke the Controller"""
        tmpl_context.w = WidgetBunch()
        try:
            return TGController.__call__(self, environ, start_response)
        finally:
            pass
