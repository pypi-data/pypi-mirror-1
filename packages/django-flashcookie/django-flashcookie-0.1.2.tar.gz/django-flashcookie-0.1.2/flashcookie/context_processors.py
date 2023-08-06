from django.utils import simplejson
from django.http import HttpResponse

def flash_context(request):
    flash = None
    if 'djangoflashcookie' in request.COOKIES:
        flash = simplejson.loads(request.COOKIES['djangoflashcookie'])
    return {'flash': flash}
