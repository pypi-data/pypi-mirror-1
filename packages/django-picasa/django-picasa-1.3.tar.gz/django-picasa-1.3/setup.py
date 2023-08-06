"""
$Id$

"""

from setuptools import setup, find_packages

version = '1.3'


LONG_DESCRIPTION = """
How to use django-googledata.picasa
--------------------------


I'm pretty useless at documentation so I will just guide you through how I use these components in my web site. 

Prerequisites
------------

Before you start you will need to install google's python api. easy_install will do that for you. 

Installing
--------
Okay lets go. Either do:: 
	easy_install django-picasa
	
Or download the distribution file into your temp or just check out the picassa module into your project's directory. Run python setup.py::
	C:\temp>
	C:\temp>python setup.py install --install-purelib="C:\your_project"
	running install
	running build
	running build_py
	creating build
	creating build\lib
	creating build\lib\picasa
	copying picasa\fields.py -> build\lib\picasa
	copying picasa\storage.py -> build\lib\picasa
	copying picasa\__init__.py -> build\lib\picasa
	running install_lib
	creating C:\your_project_root\picasa
	copying build\lib\picasa\fields.py -> C:\your_project\picasa
	copying build\lib\picasa\storage.py -> C:\your_project\picasa
	copying build\lib\picasa\__init__.py -> C:\your_project\picasa
	byte-compiling C:\your_project\picasa\fields.py to fields.pyc
	byte-compiling C:\your_project\picasa\storage.py to storage.pyc
	byte-compiling C:\your_project\picasa\__init__.py to __init__.pyc
	running install_egg_info
	Writing C:\your_project_root\django-googledata-1.0-py2.5.egg-info


settings.py
-----------

Add the framework to the INSTALLED_APPS tuple of your projects settings.py file::
	INSTALLED_APPS = (
	    'django.contrib.auth',
	    'django.contrib.contenttypes',
	    'django.contrib.sessions',
	    'django.contrib.sites',
	    'django.contrib.admin',
	    'examplesite.archive',
	    'picasa'
	)


Then add to the settings.py file your PICASA_STORAGE_OPTIONS::
	PICASA_STORAGE_OPTIONS = {
		'email':'thanosv@gmail.com',
		'source':'thanos',
		'password':'mypassword',
		'userid':'thanosv',
		'cache': True}
	
Where: 
	email is your Picasa account id. 
	source is a string you will use to identify how the images where added to your Picasa account. 
	userid is the actual Picassa account that the images will stored in. It doesn't have to be your account just any account you have the access to. 
	cache is weather you want to use Django's caching back-end. Usually it's worth it. 

If you have set cache to true they you might want to add something like this::
	CACHE_BACKEND = "locmem://?timeout=30&max_entries=400"
	
models.py
---------

Now you are done with the settings.py file you can replace the ImageFields? with the picasa field in your models::

	from picasa import  PicasaField
	class Image(models.Model):
		photo = PicasaField( )

Try it out by uploading an image through your admin page and then visit your Picasa account. You will see the uploaded image in your Drop Box.  Added a upload_to='media':: 
	photo = PicasaField( upload_to='media')

and it will upload the file into an album called media, if the album doesn't exist it will be created. 

admin.py
--------

The default admin representaion of your image will be handled by the AdminFileWidget which will just show the value of PicasaField.url of the containing web page in your Picasa account. It's useful but would be better to see a linked thumbnail. To do that you need to override the PicasaField with PicasaAdminImageWidget. To do that import the widget in your admin.py module and add it to an formfield_overrides dictionary: :

By default PicasaAdminImageWidget? generates a 64 pixel icon. The sizes available are:: 
	class PicasaFieldFile(ImageFieldFile):
		SIZES = (32, 48, 64, 72, 94, 104, 110, 128, 144, 150, 160, 200, 220, 288, 320, 400, 512, 576, 640, 720, 800, 912, 1024, 1152, 1280, 1440, 1600)

You can override the class attribute SIZE to change the thumbnail's size::
	class ImageWidget(PicasaAdminImageWidget):
		SIZE='48'
		
	class ImageAdmin(admin.ModelAdmin):
		formfield_overrides = {PicasaField: {'widget': ImageWidget},}

views.py
--------

Using the above demo model here is a quick view::
	def images(request):
		return render_to_response('archive/images.html', {'images':Image.objects})

Here is its corresponding template (templates/archive/images.html) ::
	<h2>Image List</h2>
	{% for image in images.all %}
		<a href="{{image.photo.url}}"><img src="{{image.photo.src}}" width="300"/></a><br/>
	{% endfor %}

and the html it produces::

	<h2>Image List</h2>
		<a href="http://picasaweb.google.com/thanosv/Media04#5434869420740374642"><img src="http://lh6.ggpht.com/_w0eENG7V9Qg/S2yI8Wfc8HI/AAAAAAAAAdQ/xrYdkgQF8r0/itunesscreenshot.jpg" width="300"/></a><br/>
		<a href="http://picasaweb.google.com/thanosv/Media04#5435910379245055122"><img src="http://lh3.ggpht.com/_w0eENG7V9Qg/S3A7sHHCrJI/AAAAAAAAAdw/QMY9OIviHB0/thanos.jpg" width="300"/></a><br/>

Different Sizes 
--------------

Although this HTML saves your site a lot of bandwidth your images are at the mercy of the browsers resizes and when the original images are large will still be slow to download. 

Changing the image source variables to indicate the size they need by using image.photo.src_300 instead of image.photo.src gets Picasa to do the resizing and greatly speeds up the download. requesting an image of the width 300 will in fact get you 320, which is the next available size up::
	<h2>Image List</h2>
	{% for image in images.all %}
		<a href="{{image.photo.url}}"><img src="{{image.photo.src_300}}" width="300"/></a><br/>
	{% endfor %}

And its HTML::
	<h2>Image List</h2>
		<a href="http://picasaweb.google.com/thanosv/Media04#5434869420740374642"><img src="http://lh6.ggpht.com/_w0eENG7V9Qg/S2yI8Wfc8HI/AAAAAAAAAdQ/xrYdkgQF8r0/s320/itunesscreenshot.jpg" width="300"/></a><br/>
		<a href="http://picasaweb.google.com/thanosv/Media04#5435910379245055122"><img src="http://lh3.ggpht.com/_w0eENG7V9Qg/S3A7sHHCrJI/AAAAAAAAAdw/QMY9OIviHB0/s320/thanos.jpg" width="300"/></a><br/>

Possible Problems
----------------

If you are behind a proxy and you get the following error when you try an upload an image:: 
	gaierror at /admin/archive/image/add/
	(11001, 'getaddrinfo failed')

Check that you have set both HTTP_PROXY and HTTPS_PROXY. HTTPS_PROXY can usually be set to the same host as HTTP_PROXY.

Please see http://code.google.com/p/django-googledata/ for more information.
"""

setup(name='django-picasa',
	licience = 'Apache License 2.0',
	platform = 'Any',
	version=version,
	author='Thanos Vassilakis',
	author_email='thanos@syntazo.com',
	url='http://code.google.com/p/django-googledata/',
	packages=find_packages(),
	include_package_data=True,
	zip_safe=False,
	description="""A module of django components that give you picasa storage, picasa fileds and admin fields.""",
	long_description = LONG_DESCRIPTION, 
	install_requires = ['gdata>=2.0.7',],
	classifiers=[
		"Development Status :: 5 - Production/Stable", 
		"Environment :: Web Environment",
		"Framework :: Django", 
		"Intended Audience :: Developers", 
		"License :: OSI Approved :: Apache Software License", 
		"Operating System :: OS Independent", 
		"Programming Language :: Python",
		"Topic :: Internet :: WWW/HTTP :: Dynamic Content :: CGI Tools/Libraries",
		"Topic :: Software Development :: Libraries :: Python Modules",
	],
	keywords='picassa,storage,images,photos,django,google',
	)
