from django.utils import simplejson
from django.http import HttpResponse

def flash_context(request):
    flash = None
    if 'flashcookie' in request.COOKIES:
        try:
            flash = simplejson.loads(request.COOKIES['flashcookie'])
        except ValueError:
            pass
    return {'flash': flash}
