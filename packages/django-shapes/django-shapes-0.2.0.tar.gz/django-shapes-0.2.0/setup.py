from distutils.core import setup

version = '0.2.0'
app = 'shapes'
description = 'Upload and export shapefiles using GeoDjango.'
url = 'http://bitbucket.org/springmeyer/django-%s' % app

setup(name='django-%s' % app,
      version=version,
      description=description,
      author='Dane Springmeyer',
      author_email='dbsgeo@gmail.com',
      url=url,
      download_url='%s/get/%s.tar.gz' % (url,version),
      packages=[app, "%s/views" % app],
      package_data={app:["templates/*.html"]},
      classifiers=[
          'Development Status :: 4 - Beta',
          'Environment :: Web Environment',
          'Framework :: Django',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: BSD License',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
          'Topic :: Scientific/Engineering :: GIS',
          'Topic :: Utilities'],
      )
