from django.utils import simplejson
from django.http import HttpResponse

def flash_context(request):
    flash = None
    if 'flash' in request.COOKIES:
        flash = simplejson.loads(request.COOKIES['flash'])
    return {'flash': flash}
