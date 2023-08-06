from django.utils import simplejson

class Flash(dict):
 
    def __setitem__(self, key, msg):
        self.setdefault(key, []).append(msg)
 

class FlashMiddleware(object):

    def _set_messages(self, request, response):
        """
        serialize data to json and put it in coockies
        """
        data = simplejson.dumps(request.flash)
        response.set_cookie('flash', data)

    def process_request(self, request):
        """
        Create empty request.flash attribute for later items assigments in views
        """
        request.flash = Flash()
 
    def process_response(self, request, response):
        """
        if request.flash have data, put it to cookies,
        delete previous cookie if no data in request.flash
        """
        if hasattr(request, 'flash') and len(request.flash):
            self._set_messages(request, response)
        else:
            response.delete_cookie('flash')
        return response
