import os
from django.db import models

from picasa import  PicasaField

def choices():
    from picasa import PicasaStorage
    storage= PicasaStorage()
    return [(a.title.text,a.title.text) for a in storage.albumsFromUser()]

def get_Album(instance, filename):
    album = str(instance.album)
    return os.path.join(album, filename)

class Image(models.Model):
    album = models.CharField(max_length=50, choices = choices())
    mediaPhoto = PicasaField( upload_to=get_Album)
    dropBoxPhoto = PicasaField()
    
    def __unicode__(self):
        return self.dropBoxPhoto.url
