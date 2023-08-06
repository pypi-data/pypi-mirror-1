import Image
import cherrypy
import logging

from turbogears import controllers, expose

from tempfile import TemporaryFile

from widgets.file_field import session

log = logging.getLogger("file_fields.controllers")

def file_generator(file, base64=False):
    file.seek(0)
    if base64:
        file_ = TemporaryFile()
        file_.write(file.read().decode('base64'))
        file = file_
        file.seek(0)
    for i in file:
        yield i

class PicServer(controllers.Controller):
    @expose()
    def index(self, id):
        file = session.get(id)
        if file:
            file_ = file.file
            file_.seek(0)
            if file.base64:
                file_ = file.validator.b64decode_file(file_)
            try:
                # debe haber una mejor manera de hacer esto
                image = Image.open(file_)
            except IOError, e:
                log.warning('PicServer: Error opening image (%s) in ' \
                            'temporary file (%s) error (%s)' % 
                                (id, file_.name, e))
                return ''
            format = 'image/%s' % image.format.lower()
            headers = cherrypy.response.headers
            headers['Content-Type'] = format
            headers['Content-Length'] = file.size
            return file_generator(file_)
        else:
            log.warning('PicServer: File not found (%s)' % id)
        return ''

class FileServer(controllers.Controller):
    @expose()
    def index(self, id):
        file = session.get(id)
        if file:
            headers = cherrypy.response.headers
            headers['Content-Type'] = 'application/x-download'
            headers['Content-Length'] = file.size
            headers['Content-Disposition'] = \
                'attachment; filename="%s"' % file.name
            headers['Pragma'] = 'public' # IE ssl fix (doesn't get the fname)
            return file_generator(file.file, file.base64)
        else:
            log.warning('FileServer: File not found (%s)' % id)
        return ''
