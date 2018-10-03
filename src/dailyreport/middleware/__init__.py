import time

#from django.conf import settings
#from django.utils.cache import patch_vary_headers
#from django.utils.http import cookie_date
#from django.utils.importlib import import_module
#from user_activity import ActivityMiddleware

class Checker(object):
    def process_request(self, request):
        #print request.META
        #print request.method
        #print request.path
        #print request.REQUEST.keys()
        #print request.raw_post_data
        pass

    def process_response(self, request, response):
        #print response
        return response

    