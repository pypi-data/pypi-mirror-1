import httplib, os, traceback
from urllib import urlopen
from urlparse import urlparse

from django.conf import settings
from django.core.cache import cache
from django.core.files.storage import Storage
from django.core.files.base import File

import gdata.photos.service
import gdata.media
import gdata.geo
from gdata.photos import AlbumEntry, PhotoEntry
import imghdr



class PicasaStorageException(Exception):
    pass

		
class DummyCache:
	def get(self, id): pass
	def set(self, id, value, *timeout): pass


class PicasaStorage(Storage):
	EMAIL_KEY='email'
	SOURCE_KEY='source'
	PASSWORD_KEY='password'
	USER_KEY='userid'
	CACHE_KEY='cache'
	CACHE_TIMEOUT=30
	CACHE_DEFAULT=False
	
	cache = DummyCache()
	
	def __init__(self, options=None):
		self.options = options or settings.PICASA_STORAGE_OPTIONS
		if self.options.get(self.CACHE_KEY, self.CACHE_DEFAULT):
			self.cache = cache
		self.userid = self.options[self.USER_KEY]
	
	_gdclient=None
	def getGData(self):
		if self._gdclient is None:
			self._gdclient = self.login(**self.options)
		return self._gdclient
		
	gdclient = property(getGData)

	def exists(self, filename):
		try:
			photo = self.url(filename)
			return True
		except gdata.photos.service.GooglePhotosException, e:
			if e[0] not in (404,400):
				import traceback
				traceback.print_exc()
			return False

	def _open(self, filename, mode):
		return urlopen(self.url(filename))

	def delete(self, name):
		pass
		
	def _save(self, name, content):
		album_name, image_name = os.path.split(name)
		if not album_name:
			album_name = 'default'
		else:
			album = self.albumFromTitle(album_name)
			if not album:
				print 'inserting album', album_name
				album = self.insertAlbum(album_name)
			album_name = album.gphoto_id.text
		print 'inserting photo', album_name, image_name
		content.seek(0)
		what = 'image/'+imghdr.what(image_name, content.file.read(2048))
		content.seek(0)
		album_url= '/data/feed/api/user/%s/albumid/%s' % (self.userid, album_name)
		photo = self.gdclient.InsertPhotoSimple(album_url, os.path.splitext(image_name)[0], 'Uploading from %s' % self.gdclient.source, content.file, content_type=what)
		content.close()
		id = photo.id.text
		self.cache.set(id, photo)
		return id
		
	def size(self, name):
		return self.get('size:'+id, self.getSize)
		
	def getSize(self, id):
		url = self.url(id)
		u = urlparse(url)
		conn = httplib.HTTPConnection(u.hostname)
		conn.request('HEAD', u.path)
		resp = conn.getresponse()
		fsize = int(resp.getheader('content-length'))
		return fsize

	def url(self, filename):
		return self.entry(filename).GetMediaURL()
		
	def entry(self, id):
		return self.get('entry', id, self.gdclient.GetEntry)
			
	def albumFromTitle(self, title):
		return self.get('entry', title, self.searchAlbums)
		
	def searchAlbums(self, title):
		for a in self.albumsFromUser():
			if a.title.text == title:
				return a	
		
	def login(self, email, password, source, userid='default', **kwa):
		gdclient = gdata.photos.service.PhotosService()
		gdclient.email = email
		gdclient.password = password
		gdclient.source = source
		gdclient.ProgrammaticLogin()
		return gdclient
	
	def albumsFromUser(self, userid=None):
		x = self.gdclient
		if userid is None:
			userid = self.userid
		return self.gdclient.GetUserFeed(user= userid).entry
		
	def insertAlbum(self, title, description=''):
		return self.gdclient.InsertAlbum(title, description)
		
	def get(self, which, id, getter, *args, **kwa):
		key = which+':'+id
		obj = self.cache.get(key)
		#print 'CACHE', key, obj
		if obj is None:
			obj = getter(id, *args, **kwa)
			self.cache.set(key, obj)
			#print 'NEW OBJ', key, obj
		return obj