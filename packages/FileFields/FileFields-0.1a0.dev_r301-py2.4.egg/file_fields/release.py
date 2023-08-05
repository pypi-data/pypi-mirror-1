# Release information about FileFields

version = "0.1a0"

description = "File and Image upload fields for forms."
long_description = """Right now this package provides 2 widgets, FileField and ImageField.
These widgets support file uploading with server side caching. That means that if some other field in the form fails validation, the user wont have to upload the file again. Instead they get the information of the file they included or a thumbnail of the image if it's an ImageField. An option to remove the file from the form is given too.
If Lightbox is installed (optional), the full size images will be displayed with it (non popup image viewer).
Also an animation removing the file attached to the form will be shown if Scriptculous is installed (optional).
The server side caching is done using the TemporaryFile class from the official Python tempfile module. It's a secure way to store files on a platform independent way. The files are cleared when they are not used anymore.
"""
author = "Claudio Martinez"
email = "claudio.s.martinez@gmail.com"
# copyright = "Vintage 2006 - a good year indeed"

# if it's open source, you might want to specify these
# url = "http://yourcool.site/"
# download_url = "http://yourcool.site/download"
license = "MIT"
