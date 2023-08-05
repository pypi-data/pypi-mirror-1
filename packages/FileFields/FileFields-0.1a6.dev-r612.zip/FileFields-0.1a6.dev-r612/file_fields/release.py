# Release information about FileFields

version = "0.1a6"

description = "File and Image upload fields for forms."
long_description = """Right now this package provides 2 widgets, FileField and ImageField.
These widgets support file uploading with server side caching. That means that 
if some other field in the form fails validation, the user wont have to upload 
the file again. Instead they get the information of the file they included or a 
thumbnail of the image if it's an ImageField. An option to remove the file from 
the form is given too.

The ImageField has a thumbnail preview and allows size validation and automatic 
resizing when dimensions get past certain values (this isn't enabled by 
default).

If Lightbox is installed (optional), the full size images will be displayed 
with it (non popup image viewer).
Also an animation removing the file attached to the form will be shown if 
Scriptculous is installed (optional).
The server side caching is done using the TemporaryFile class from the official 
Python tempfile module. It's a secure way to store files on a platform 
independent way. The files are cleared when they are not used anymore.

The widgets need a controller that will be the file server for the download 
links and images previews. You can import the controllers from 
file_fields.controllers (PicServer and FileServer) and specify the url on the 
widget constructors (file_server_url, image_server_url)

The easiest and recommended way is enabling the extension your dev.cfg, 
prod.cfg or app.cfg adding:

file_field_server.on = True"""
author = "Claudio Martinez"
email = "claudio.s.martinez@gmail.com"
# copyright = "Vintage 2006 - a good year indeed"

# if it's open source, you might want to specify these
# url = "http://yourcool.site/"
# download_url = "http://yourcool.site/download"
license = "MIT"
