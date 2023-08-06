from django.conf import settings
FILE_STORAGE_ROOT = getattr(settings, 'FILE_STORAGE_ROOT', settings.MEDIA_ROOT)
USE_XSENDFILE = getattr(settings, 'FILE_USE_XSENDFILE', False)