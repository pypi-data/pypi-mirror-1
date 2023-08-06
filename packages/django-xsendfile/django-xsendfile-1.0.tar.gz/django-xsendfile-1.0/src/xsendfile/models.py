import os.path
import settings
from datetime import datetime
from django.core.files.storage import FileSystemStorage
from django.db import models
from django.http import HttpResponse, HttpResponseForbidden
from django.utils.translation import ugettext_lazy as _
from email.header import Header

try:
    import magic
except ImportError:
    Magic = type('Magic', (object,), {})
    Magic.from_file = lambda self, x: 'application/octet-stream;0'
    mime = Magic()
else:
    mime = magic.Magic(mime=True)

def get_file_upload_to(instance, filename):
    '''
    The upload path can be specified in the model by writing an instance.get_file_upload_to method.
    
    The method should accept the filename as its argument, and should return a unix path that will
    be appended to settings.FILE_STORAGE_ROOT.
    By default the system falls back on "Year/Month" 
    '''
    try:
        return instance.get_file_upload_to(filename)
    except AttributeError:
        return '%s/%s' % (datetime.today().strftime('%Y/%m'), filename)

class XSendFile(models.Model):
    
    check_permissions = []
    
    file = models.FileField(upload_to=get_file_upload_to, verbose_name=_('File'), 
                storage=FileSystemStorage(location=settings.FILE_STORAGE_ROOT))
    filetype = models.CharField(max_length=255, verbose_name=_('File type'), blank=True, editable=False)
    size = models.PositiveIntegerField(verbose_name=_('File size (in bytes)'), null=True, editable=False)
    comment = models.CharField(verbose_name=_('Comment'), max_length=50, blank=True)
    created = models.DateTimeField(auto_now_add=True, editable=False)
    
    class Meta:
        verbose_name = _('File')
        verbose_name_plural = _('Files')
        ordering = ('created', 'file')

    def __unicode__(self):
        return u'File: %s' % self.file.name
    
    def get_absolute_url(self):
        from django.core.urlresolvers import reverse
        if settings.USE_XSENDFILE:
            return reverse('xsendfile_get', kwargs={'file_id': self.pk})
        return self.file.url
    
    def save(self, force_insert=False, force_update=False):
        super(XSendFile, self).save(force_insert, force_update)
        self.filetype = mime.from_file(self.file.path).split(';')[0]
        self.size = os.path.getsize(self.file.path) 
        super(XSendFile, self).save()
        
    def get_filename(self):
        return os.path.basename(self.file.name)
    
    def get_xsendfile(self):
        '''
        Return a HttpResponse to access an AbstractFile via mod_xsendfile
        '''
        rsp = HttpResponse()
        rsp['Content-Type'] = self.filetype
        rsp['Content-Disposition'] = 'attachment; filename="%s"' % Header(self.get_filename(), 'utf8').encode()
        rsp["X-Sendfile"] = self.file.path
        rsp['Content-length'] = os.path.getsize(self.file.path)
        return rsp

    def get(self, request):
        '''
        Checks whether the file can be accessed with the request's privileges.
        To be overwritten.
        '''
        if all(map(lambda permission: permission(self, request), self.check_permissions)):
            return self.get_xsendfile()
        return HttpResponseForbidden(_('You are not allowed to access this file'))
