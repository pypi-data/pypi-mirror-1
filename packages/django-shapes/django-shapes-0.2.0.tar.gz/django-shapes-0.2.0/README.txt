django-shapes
-------------

Working with Shapefiles in Django using GeoDjango.

To enable this application within a larger GeoDjango Project:

 - Copy or checkout the `shapes` folder into your project folder.
 
 - Add `shapes` to your INSTALLED APPS.
 
 - Check out the docs/ folder to see how to set up exports and uploads
  
 - Add SHP_UPLOAD_DIR = '/some/path' in your setting.py for the upload functionality.
 
 - Note: the ShpResponder class, as of 0.2.0 defaults to using OGR's native python bindings
   which should be available if GDAL was compiled with --with-python
    

Working with mercurial
----------------------

$ hg pull

$ hg update

$ hg ci -m "message" <file>

$ hg push


More info
---------

http://www.bitbucket.org/springmeyer/django-shapes/