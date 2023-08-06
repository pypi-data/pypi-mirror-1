from django.utils import simplejson


def flash_context(request):
    flash = request.flash
    if flash:
        request.flash = {}

    if 'flashcookie' in request.COOKIES:
        try:
            flash = simplejson.loads(request.COOKIES['flashcookie'])
        except ValueError:
            pass
    return {'flash': flash}
