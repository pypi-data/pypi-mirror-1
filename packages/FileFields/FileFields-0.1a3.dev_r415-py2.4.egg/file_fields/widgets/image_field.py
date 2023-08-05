# -*- coding: utf-8 -*-

import Image
import cherrypy
import logging

from turbogears import validators, widgets, url

from tempfile import TemporaryFile

from file_field import FileField, FileValidator

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
        value = super(ImageValidator, self)._to_python(value, state)
        if value and not value.get('image_processed'):
            if self.base64:
                value['file'] = self.b64decode_file(value['file'])
                value['base64'] = False
            
            value['file'].seek(0)
            try: # verificamos que PIL reconozca el formato de la imagen
                image = Image.open(value['file'])
            except:
                value.clear()
                raise validators.Invalid(self.message('unsupported', state),
                                         value, state)
            
            #verificamos el tamaño de la imagen
            if self.max_dimensions != (0, 0) and \
               (self.max_dimensions[0] < image.size[0] or \
                self.max_dimensions[1] < image.size[1]):
                if not self.resize_if_bigger:
                    value.clear()
                    raise validators.Invalid(self.message('too_big', state),
                                             value, state)
                value['file'] = self.resize(value['file'], self.max_dimensions)
                
                old_id = value['id']
                cherrypy.session.pop(value['id'])
                
                value['id'] = value['md5'] = self.get_md5_file(value['file'])
                value['size'] = self.get_file_size(value['file'])
                
                cherrypy.session[value['id']] = value
                
            cherrypy.session[self.get_thumb_session_key(value['id'])] = \
                self.get_thumbnail(value['file'])
                
            value['image_processed'] = True
        elif not value:
            return ''
        if not value.get('base64') and self.base64:
            value['file'] = self.b64encode_file(value['file'])
            value['base64'] = True
        value['file'].seek(0)
        return value
    
    def get_thumb_session_key(self, id):
        return '%s_%s_%s_thumb' % (id, self.thumb_dimensions[0],
                                   self.thumb_dimensions[1])
    
    def _from_python(self, value, state):
        value = super(ImageValidator, self)._from_python(value, state)    
        cherrypy.session[self.get_thumb_session_key(value['id'])] = \
            self.get_thumbnail(value['file'])
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
        info['size'] = file.tell()
        info['file'] = file
        return info

# Como mostrar una imagen inline
#<img src="data:${thumbnail.type};base64,${thumbnail.data}" />

class ImageField(FileField):
    template = """
    <div xmlns:py="http://purl.org/kid/ns#">
        <input type="hidden" id="${field_id}.id" name="${name}.id"
            value="${isinstance(value, dict) and value.get('id') or ''}"/>
        <input type="file" id="${field_id}.file" name="${name}.file"/>
        <div py:if="value_of('value')" id="${field_id}_pic">
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
                    ${lightbox.display(img_url, thumb_url=thumb_url)}
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
        if d['value']:
            d['lightbox'] = self.lightbox
            d['img_url'] = url(self.image_server_url, id=d['value']['id'])
            d['thumb_url'] = url(self.image_server_url, 
                                 id=(self.validator.get_thumb_session_key(
                                                        d['value']['id'])))

class ImagePreview(ImageField):
    template = """
    <div xmlns:py="http://purl.org/kid/ns#">
        <div py:if="value_of('value')" id="${field_id}_pic">
            <div style="display: block; text-align: center">
                <img src="${thumb_url}" border="0" />
            </div>
        </div>
    </div>
    """
    