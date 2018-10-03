import os, sys
#sys.path.append('/usr/lib/python2.6/site-packages/dailyreport')
os.environ['DJANGO_SETTINGS_MODULE'] = 'dailyreport.settings'

import django.core.handlers.wsgi

application = django.core.handlers.wsgi.WSGIHandler()