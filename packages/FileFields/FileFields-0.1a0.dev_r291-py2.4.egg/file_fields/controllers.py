import Image
import cherrypy

from turbogears import controllers, expose

from tempfile import TemporaryFile

def file_generator(file, base64):
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
        file = cherrypy.session.get(id)
        if file:
            try:
                # debe haber una mejor manera de hacer esto
                file['file'].seek(0)
                image = Image.open(file['file'])
                format = 'image/%s' % image.format.lower()
            except IOError:
                return ''
            headers = cherrypy.response.headers
            headers['Content-Type'] = format
            headers['Content-Length'] = file['size']
            return file_generator(file['file'], file.get('base64'))
        return ''

class FileServer(controllers.Controller):
    @expose()
    def index(self, id):
        file = cherrypy.session.get(id)
        if file:
            headers = cherrypy.response.headers
            headers['Content-Type'] = 'application/x-download'
            headers['Content-Length'] = file['size']
            headers['Content-Disposition'] = \
                'attachment; filename=%s' % file['name']
            headers['Pragma'] = 'public' # IE ssl fix (doesn't get the fname)
            return file_generator(file['file'], file.get('base64'))
        return ''
