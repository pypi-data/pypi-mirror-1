GalleryRemote

Implementation of the Gallery Remote Protocol in a Python class.

See docstrings for more information, and here for the Gallery
Remote protocol specification:
http://codex.gallery2.org/Gallery_Remote:Protocol

Example usage:
from galleryremote import Gallery
my_gallery = Gallery('http://www.yoursite.com/gallery2', 2)
my_gallery.login('username','password')
albums = my_gallery.fetch_albums()

