from django.db.models.fields.files import  FieldFile,FileField
from picasa.storage import PicasaStorage
from django.contrib.admin.widgets import AdminFileWidget
from django.utils.safestring import mark_safe


import re

__all__ = ['PicasaField','PicasaAdminImageWidget']

class PicasaAdminImageWidget(AdminFileWidget):
    # A FileField Widget that displays an image instead of a file path
    # if the current file is an image.
    storage = PicasaStorage()
    SIZE=64
    def render(self, name, photo, attrs=None):
        output = []
        if photo:
            src = photo.src(self.SIZE)
            try:            # is image
                output.append(r'<a target="_blank" href="%s"><img src="%s" align="left" valign="middle" /></a>' % (photo.url, src))
                #output.append('%s <a target="_blank" href="%s">%s</a> <br/>%s' % (_('Currently:'), file_path, file_name, _('Change:')))
            except:
                output.append('Not an image ')
        else:
            output.append('Add:')
        output.append(super(AdminFileWidget, self).render(name, photo, attrs))
        return mark_safe(u''.join(output))


from bisect import bisect
class PicasaFieldFile(FieldFile):
    SIZES = (32, 48, 64, 72, 94, 104, 110, 128, 144, 150, 160, 200, 220, 288, 320, 400, 512, 576, 640, 720, 800, 912, 1024, 1152, 1280, 1440, 1600)
    sizeRE = re.compile(r'src_(\d+)$')
    def __init__(self, *args, **kwargs):
        super(PicasaFieldFile, self).__init__(*args, **kwargs)
        self.storage = PicasaStorage()
        
    def photo(self):
        return self.storage.entry(self.name)

    def __getattr__(self, name):
        match = self.sizeRE.match(name)
        if match:
            size = int(match.group(1))
            return self.src(size=size)
        return super(PicasaFieldFile, self).__getattr__(name)
            
    def src(self, size=None):
        img_url = self.storage.url(self.name)
        if size is not None:
            try:
                size = self.SIZES[bisect(self.SIZES, size-1)]
            except IndexError:
                size = self.SIZES[-1]
            url, img = img_url.rsplit ('/',1)
            return '%s/s%d/%s' %(url, size, img)
        return  img_url
    
    def _url(self):
        return  self.photo().GetHtmlLink().href
    url = property(_url)
        
        
        
    
    
        

class PicasaField(FileField):
    attr_class = PicasaFieldFile
    def __init__(self, *args,  **kwargs):
        kwargs.setdefault('upload_to', 'default')
        super(PicasaField, self).__init__(*args, **kwargs)
    
    def south_field_triple(self):
        """
        Return a suitable description of this field for South.
        """
        from south.modelsinspector import introspector
        field_class = "django.db.models.fields.files.FileField"
        args, kwargs = introspector(self)
        return (field_class, args, kwargs)
