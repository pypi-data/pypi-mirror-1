# -*- coding: utf-8 -*-

# Es al cohete convertir hacia y de base64. Hay que tener los filehandles 
#   abiertos y listo...
# Limitar el tamaño del upload.
# Deberia poder recibir todos los datos para no tener que calcular nada y
#   y hacerlo super liviano.
# Tambien tendria que en data recibir una funcion o algo por el estilo
#   para hacerlo lazy.

import cherrypy

import md5

import logging

from os.path import basename

from turbogears import widgets, validators, url
from turbogears.util import Bunch

from tempfile import TemporaryFile

log = logging.getLogger("file_fields.widgets.file_field")

class FileValidator(validators.FancyValidator):
    messages = {'file_needed': 'A file is needed'}
    
    def __init__(self, base64=False, *args, **kw):
        super(FileValidator, self).__init__(*args, **kw)
        self.base64 = base64
    
    def get_md5(self, data):
        hash = md5.new()
        hash.update(data)
        return hash.hexdigest()
        
    def get_md5_file(self, file):
        file.seek(0)
        return self.get_md5(file.read())
    
    def make_temp_file(self, data):
        file = TemporaryFile()
        file.write(data)
        file.seek(0)
        return file
        
    def get_file_size(self, file):
        file.seek(0, 2)
        size = file.tell()
        file.seek(0)
        return size
    
    def b64encode_file(self, file):
        file.seek(0)
        file = self.make_temp_file(file.read().encode('base64'))
        return file
    
    def b64decode_file(self, file):
        file.seek(0)
        file = self.make_temp_file(file.read().decode('base64'))
        return file
    
    def basename(self, name):
        name = basename(name)
        if name.split('\\'): # IE bug fix (sends comlpete path as filename) and
                             # basename won't clear it if its on a linux server
            return name.split('\\')[-1]
        return name
    
    def _to_python(self, value, state):
        file = None
        if value['file'].filename:
            # nuevo archivo desde el formulario
            info = value['file'] # FieldStorage()
            # inicializamos la sesion
            value.clear()
            value['id'] = value['md5'] = self.get_md5_file(info.file)
            value['type'] = info.type
            value['name'] = self.basename(info.filename)
            value['size'] = self.get_file_size(info.file)
            value['file'] = info.file
            cherrypy.session[value['id']] = value
        else:
            if value['id']:
                # hay que sacar el diccionario de la session
                id = value['id']
                value.clear()
                value.update(cherrypy.session[id])
            else:
                # no hay archivo en sesion ni llego ninguno en el formulario
                value.clear()
                if self.not_empty:
                    raise validators.Invalid(self.message('file_needed', 
                                                          state),
                                             value, state)
                return ''
        if not value.get('base64') and self.base64:
            value['file'] = self.b64encode_file(value['file'])
            value['base64'] = True
        value['file'].seek(0)
        value['validator'] = self
        return value
        
    def _from_python(self, value, state):
        # TODO: refactorear esto
        if isinstance(value, dict):
            type_ = value['type']
            name = value['name']
            # this has to be last
            value = value.get('file') or value.get('data')
            if hasattr(value, 'read'):
                value.seek(0)
                value = value.read()
        else:
            # if don't get a hint we can't guess this data
            type_ = ''
            name = ''
            
        if self.base64:
            value = value.decode('base64')
            
        file_ = self.make_temp_file(value)
        hash = md5.new()
        hash.update(value)
        size = len(value)
        
        # inicializamos la sesion
        value = dict()
        value['id'] = value['md5'] = hash.hexdigest()
        value['size'] = size
        value['file'] = file_
        value['type'] = type_
        value['name'] = name
        value['validator'] = self
        cherrypy.session[value['id']] = value
        
        return value

class FileField(widgets.FormField):
    template = """
    <div xmlns:py="http://purl.org/kid/ns#">
        <input type="hidden" id="${field_id}.id" name="${name}.id"
            value="${isinstance(value, dict) and value.get('id') or ''}"/>
        <input type="file" id="${field_id}.file" name="${name}.file"/>
        <div py:if="value_of('value')" id="${field_id}_info">
            <div style="float: right; font-size: small">
                <a href="${file_url}" style="font-size: small">
                    Download
                </a> | 
                <span py:if="scriptaculous"> 
                    <a href="#" onclick="document.getElementById('${field_id}.id').value=''; new Effect.BlindUp(document.getElementById('${field_id}_info'));">
                        Delete File
                    </a>
                </span>
                <span py:if="not scriptaculous"> 
                    <a href="#" onclick="document.getElementById('${field_id}.id').value=''; document.getElementById('${field_id}_info').style.display='none';">
                        Delete file
                    </a>
                </span>
            </div>
            <div py:if="value['name']">
                <b>Name:</b> ${value['name']}
                
            </div>
            <div py:if="value['size']">
                <b>Size:</b> ${value['size']}
            </div>
            <div py:if="value['type']">
                <b>Type:</b> ${value['type']}
            </div>
            <div py:if="value['md5']">
                <b>MD5:</b> ${value['md5']}
            </div>
        </div>
    </div>
    """
    
    file_upload = True
    scriptaculous = None
    css = []
    javascript = []
    
    def __init__(self, name='', base64=False, use_scriptaculous=True, 
                 file_server_url='/file_server/', *args, **kw):
        super(FileField, self).__init__(name=name, *args, **kw)
        self.base64 = base64
        self.validator = FileValidator(base64=base64)
        self.file_server_url = file_server_url
        
        if use_scriptaculous:
            try:
                from scriptaculous import scriptaculous
                self.scriptaculous = scriptaculous
                self.javascript += self.scriptaculous.javascript
            except ImportError:
                log.warning('Scriptaculous is not installed')
    
    def update_params(self, d):
        super(FileField, self).update_params(d)
        if d['value']:
            d['scriptaculous'] = self.scriptaculous
            d['file_url'] = url(self.file_server_url, id=d['value']['id'])

