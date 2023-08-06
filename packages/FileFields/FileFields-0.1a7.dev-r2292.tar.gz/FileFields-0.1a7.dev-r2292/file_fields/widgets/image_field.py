# -*- coding: utf-8 -*-

import Image
import logging

from cherrypy import request

from turbogears import validators, widgets, url

from tempfile import TemporaryFile

from file_field import FileField, FileValidator, File, session

log = logging.getLogger("file_fields.widgets.image_field")

class ImageValidator(FileValidator):
    messages = {'unsupported': 'Unsupported image format',
                'too_big': 'Image dimensions are too large',
                'file_needed': 'An image is needed'}
    
    def __init__(self, thumb_dimensions=(220, 220), base64=False, 
                 max_dimensions=(0, 0), resize_if_bigger=False, *args, **kw):
        super(ImageValidator, self).__init__(*args, **kw)
        self.base64 = base64
        self.thumb_dimensions = thumb_dimensions
        self.max_dimensions = max_dimensions
        self.resize_if_bigger = resize_if_bigger
    
    def _to_python(self, value, state):
        file = super(ImageValidator, self)._to_python(value, state)
        if file and not getattr(file, 'image_processed', None):
            if self.base64:
                file.file = self.b64decode_file(file.file)
                file.base64 = False
            
            file.file.seek(0)
            try: # verificamos que PIL reconozca el formato de la imagen
                image = Image.open(file.file)
            except:
                value = dict()
                raise validators.Invalid(self.message('unsupported', state),
                                         value, state)
            
            #verificamos el tamaño de la imagen
            if self.max_dimensions != (0, 0) and \
               (self.max_dimensions[0] < image.size[0] or \
                self.max_dimensions[1] < image.size[1]):
                if not self.resize_if_bigger:
                    value = dict()
                    raise validators.Invalid(self.message('too_big', state),
                                             value, state)
                file.file = self.resize(file.file, self.max_dimensions)
                
                old_id = file.id
                session.pop(file.id)
                
                file.id = file.md5 = self.get_md5_file(file.file)
                file.size = self.get_file_size(file.file)
                
                session[file.id] = file
            
            session[self.get_thumb_session_key(file.id)] = \
                self.get_thumbnail(file.file)
            file.image_processed = True
        if file:
            if not file.base64 and self.base64:
                file.file = self.b64encode_file(file.file)
                file.base64 = True
            file.file.seek(0)
        return file
    
    def get_thumb_session_key(self, id):
        return '%s_%s_%s_thumb' % (id, self.thumb_dimensions[0],
                                   self.thumb_dimensions[1])
    
    def _from_python(self, value, state):
        value = super(ImageValidator, self)._from_python(value, state)    
        file = session[value['id']]
        file_ = file.file
        if file.base64:
            file_ = self.b64decode_file(file_)
        session[self.get_thumb_session_key(file.id)] = \
            self.get_thumbnail(file_)
        return value
        
    def resize(self, file, dimensions):
        file.seek(0)
        image = Image.open(file)
        image.thumbnail(dimensions)
        file = TemporaryFile()
        try:
            image.save(file, format=image.format)
        except IOError:
            log.warning('There was a problem resizing the image')
        file.seek(0)
        return file
        
    def get_thumbnail(self, file):
        file = self.resize(file, self.thumb_dimensions)
        info = dict()
        file.seek(0, 2)
        file_ = File(id=None, md5=None, type=None, name=None,
                     size=file.tell(), file=file)
        return file_

# Como mostrar una imagen inline
#<img src="data:${thumbnail.type};base64,${thumbnail.data}" />

class ImageField(FileField):
    template = """
    <div xmlns:py="http://purl.org/kid/ns#">
        <input type="hidden" id="${field_id}.id" name="${name}.id"
            value="${value_of('file') and file.id or ''}"/>
        <input type="file" id="${field_id}.file" name="${name}.file"/>
        <div py:if="value_of('file')" id="${field_id}_pic">
            <span py:if="scriptaculous"> 
                <a href="#" onclick="document.getElementById('${field_id}.id').value=''; new Effect.BlindUp(document.getElementById('${field_id}_pic'));" 
                   style="float: right; font-size: small">
                    Delete Image
                </a>
            </span>
            <span py:if="not scriptaculous"> 
                <a href="#" onclick="document.getElementById('${field_id}.id').value=''; document.getElementById('${field_id}_pic').style.display='none';" 
                   style="float: right; font-size: small">
                    Delete Image
                </a>
            </span>
            <div style="display: block; text-align: center">
                <span py:if="lightbox">
                    ${lightbox.display(img_url, thumb_url=thumb_url,
                                       thumb_height=None, thumb_width=None)}
                </span>
                <span py:if="not lightbox">
                    <a href="${img_url}" target="_new">
                        <img src="${thumb_url}" border="0" />
                    </a>
                </span>
            </div>
        </div>
    </div>
    """
    
    file_upload = True
    lightbox = None
    scriptaculous = None
    css = []
    javascript = []
    
    def __init__(self, name='', thumb_dimensions=(220, 220), base64=False, 
                 max_dimensions=(0, 0), resize_if_bigger=False,
                 use_lightbox=True, image_server_url='/pic_server/', *args, 
                 **kw):
        super(ImageField, self).__init__(name=name, *args, **kw)
        self.image_server_url = image_server_url
        self.validator = ImageValidator(thumb_dimensions=thumb_dimensions,
                                        max_dimensions=max_dimensions,
                                        resize_if_bigger=resize_if_bigger,
                                        base64=base64)
        if use_lightbox:
            try:
                from lightbox.widgets import Lightbox
                self.lightbox = Lightbox()
                self.javascript += self.lightbox.javascript
                self.css += self.lightbox.css
            except ImportError:
                log.warning('Lightbox is not installed')
    
    def update_params(self, d):
        super(ImageField, self).update_params(d)
        if d.get('file'):
            d['lightbox'] = self.lightbox
            d['img_url'] = url(self.image_server_url, id=d['file'].id)
            d['thumb_url'] = url(self.image_server_url, 
                                 id=(self.validator.get_thumb_session_key(
                                                        d['file'].id)))

class ImagePreview(ImageField):
    template = """
    <div xmlns:py="http://purl.org/kid/ns#">
        <div py:if="value_of('value')" id="${field_id}_pic">
            <span py:if="lightbox">
                    ${lightbox.display(img_url, thumb_url=thumb_url,
                                       thumb_height=None,
                                       thumb_width=None)}
            </span>
            <span py:if="not lightbox">
                <img src="${thumb_url}" border="0" />
            </span>
        </div>
    </div>
    """
    