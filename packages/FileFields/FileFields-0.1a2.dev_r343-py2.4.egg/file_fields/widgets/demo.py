# -*- coding: utf-8 -*-

import cherrypy

from turbogears import expose, validate, error_handler, validators, redirect
from turbogears.widgets import TextField, TableForm, WidgetDescription

from file_fields.widgets import FileField, ImageField
from file_fields.controllers import PicServer, FileServer

def check_and_enable_sessionfilter():
    if cherrypy.request._session.session_storage is None:
        cherrypy.config.update({'session_filter.on': True})
        raise redirect('.')

class FileFieldDesc(WidgetDescription):
    full_class_name = 'file_fields.widgets.FileField'
    name = "FileField package - FileField"
    template = """
        <div>
            Click <a href="file_fields.widgets.FileField">here</a>
            to see it in action.
        </div>
    """
    
    def _get_form(self):
        return self.form
        
    def __init__(self):
        class Int(validators.Int):
            def _from_python(self, value, state):
                return value # so we can load an invalid int as default
        self.for_widget = FileField() # we add this after we enable sessions
        self.server = FileServer()
        fields = [FileField('file', file_server_url='server'),
                  TextField('fail', default='this will fail the validation', 
                            validator=Int())]
        self.form = TableForm(fields=fields, action='save')
    
    @expose(template='file_fields.widgets.file_field_desc')
    def index(self):
        check_and_enable_sessionfilter()
        return dict(form=self.form)
    
    @expose()
    @validate(form=_get_form)
    @error_handler(index)
    def save(self, **kw):
        raise redirect('../')

class ImageFieldDesc(WidgetDescription):
    full_class_name = 'file_fields.widgets.ImageField'
    name = "FileField package - ImageField"
    template = """
        <div>
            Click <a href="file_fields.widgets.ImageField">here</a>
            to see it in action.
        </div>
    """
    
    def _get_form(self):
        return self.form
        
    def __init__(self):
        class Int(validators.Int):
            def _from_python(self, value, state):
                return value # so we can load an invalid int as default
        self.for_widget = ImageField() # we add this after we enable sessions
        self.server = PicServer()
        fields = [ImageField('image', image_server_url='server'), 
                  TextField('fail', default='this will fail the validation', 
                            validator=Int())]
        self.form = TableForm(fields=fields, action='save')
    
    @expose(template='file_fields.widgets.image_field_desc')
    def index(self):
        check_and_enable_sessionfilter()
        return dict(form=self.form)
    
    @expose()
    @validate(form=_get_form)
    @error_handler(index)
    def save(self, **kw):
        raise redirect('../')

