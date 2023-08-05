# -*- coding: utf-8 -*-

# Es al cohete convertir hacia y de base64. Hay que tener los filehandles 
#   abiertos y listo...
# Limitar el tamaño del upload.
# Deberia poder recibir todos los datos para no tener que calcular nada y
#   y hacerlo super liviano.
# Tambien tendria que en data recibir una funcion o algo por el estilo
#   para hacerlo lazy.


import md5

import logging

from cherrypy import request

try:
    from cherrypy import session
except ImportError:
    from cherrypy.lib.sessions import RamSession
    session = RamSession()

from os.path import basename

from turbogears import widgets, validators, url
from turbogears.util import Bunch

from tempfile import TemporaryFile

log = logging.getLogger("file_fields.widgets.file_field")

class File(object):
    "File object for forms"
    def __init__(self, id, md5, type, name, size, file, base64=False):
        self.id = id
        self.md5 = md5
        self.type = type
        self.name = name
        self.size = size
        self.file = file
        self.base64 = base64

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
        if getattr(value['file'], 'filename', None):
            # nuevo archivo desde el formulario
            info = value['file'] # FieldStorage()
            
            # verificamos si ya procesamos este field storage
            if self.get_associated_file(info):
                file = self.get_associated_file(info)
            else:
                # es un upload nuevo, inicializamos la sesion
                md5 = self.get_md5_file(info.file)
                file = File(id=md5, md5=md5, type=info.type, file=info.file,
                            name=self.basename(info.filename),
                            size=self.get_file_size(info.file))
                session[file.id] = file
                self.associate_field_storage(info, file)
        else:
            if value['id']:
                # hay que sacar el diccionario de la session
                file = session[value['id']]
            else:
                # no hay archivo en sesion ni llego ninguno en el formulario
                if self.not_empty:
                    raise validators.Invalid(self.message('file_needed', 
                                                          state),
                                             value, state)
                return None
        if file:
            if not file.base64 and self.base64:
                file.file = self.b64encode_file(file.file)
                file.base64 = True
            file.file.seek(0)
            file.validator = self
        return file
    
    def get_associated_file(self, field_storage):
        if not hasattr(request, 'uploaded_files'):
            return None
        return request.uploaded_files.get(field_storage)
    
    def associate_field_storage(self, field_storage, file):
        '''Saves a reference of a FieldStorage pointing to the processed 
            to_python version. This is done to prevent duplicated processing on
            the same request if to_python is called multiple times on the same 
            values.'''
        if not hasattr(request, 'uploaded_files'):
            request.uploaded_files = dict()
        request.uploaded_files[field_storage] = file
        
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
        elif isinstance(value, File):
            file = value
            value = dict()
            value['id'] = file.id
            value['file'] = None
            return value
        else:
            # if don't get a hint we can't guess this data
            # FIXME: we have to remove this, we should only support
            # receiving File objects
            type_ = ''
            name = ''
            
        if self.base64:
            value = value.decode('base64')
            
        file_ = self.make_temp_file(value)
        hash = md5.new()
        hash.update(value)
        size = len(value)
        
        # inicializamos la sesion
        hash = hash.hexdigest()
        file = File(id=hash, md5=hash, size=size, file=file_, type=type_,
                    name=name)
        session[file.id] = file
        
        value = dict()
        value['id'] = hash
        value['file'] = None
        return value

class FileField(widgets.FormField):
    template = """
    <div xmlns:py="http://purl.org/kid/ns#">
        <input type="hidden" id="${field_id}.id" name="${name}.id"
            value="${value_of('file') and file.id or ''}"/>
        <input type="file" id="${field_id}.file" name="${name}.file"/>
        <div py:if="value_of('file')" id="${field_id}_info">
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
            <div py:if="file.name">
                <b>Name:</b> ${file.name}
                
            </div>
            <div py:if="file.size">
                <b>Size:</b> ${file.size}
            </div>
            <div py:if="file.type">
                <b>Type:</b> ${file.type}
            </div>
            <div py:if="file.md5">
                <b>MD5:</b> ${file.md5}
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
    
    def load_file_from_session(self, id):
        return session[id]
    
    def update_params(self, d):
        super(FileField, self).update_params(d)
        if d['value']:
            if isinstance(d['value'], dict):
                try:
                    d['file'] = self.validator.to_python(d['value'])
                except:
                    pass
            elif isinstance(d['value'], File):
                d['file'] = d['value']
            else:
                raise ValueError('Unexpected content "%s" for widget' % \
                                    d['value'])
                                    
            d['scriptaculous'] = self.scriptaculous
            
            if d.get('file'):
                d['file_url'] = url(self.file_server_url, id=d['file'].id)

