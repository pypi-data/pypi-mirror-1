#!/usr/bin/python
# -*- coding: utf-8 -*-

import settings, models
from django import test
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.urlresolvers import reverse

class XSendFile(test.TestCase):
    
    def test_default(self):
        file = SimpleUploadedFile('myfile', 'this is text', 'text/plain')
        f = models.XSendFile.objects.create(file=file)
        self.assertEqual(f.pk, 1)
        self.assertEqual(f.size, 12)
        self.assertEqual(f.filetype, 'application/octet-stream')
        str(f) # check __unicode__
        return f
        
    def test_get_xsendfile(self):
        from django.http import HttpResponse
        f = self.test_default()
        rsp = f.get_xsendfile()
        self.assertTrue(isinstance(rsp, HttpResponse))
        self.assertTrue(rsp['Content-Type'], f.filetype)
        self.assertTrue(rsp['Content-Disposition'], 'attachment; filename="%s"' % f.file.name)
        self.assertTrue(rsp["X-Sendfile"], f.file.path)
        self.assertTrue(rsp['Content-length'], f.size)
        
class ViewTest(test.TestCase):
    urls = 'xsendfile.urls'
    
    def test_basic(self):
        file = SimpleUploadedFile('myfile', 'this is text', 'text/plain')
        f = models.XSendFile.objects.create(file=file)
        models.XSendFile.check_permissions.append(lambda x,y: False)
        rsp = self.client.get(reverse('xsendfile_get', kwargs={'file_id': f.pk}))
        self.assertEqual(rsp.status_code, 403)
        
