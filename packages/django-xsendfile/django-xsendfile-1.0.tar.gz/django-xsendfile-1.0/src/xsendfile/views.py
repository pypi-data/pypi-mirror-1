from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, get_list_or_404
import models

def get_file(request, file_id):
    '''
    Return the file 
    '''
    afile = get_object_or_404(models.XSendFile, pk=int(file_id))
    return afile.get(request)