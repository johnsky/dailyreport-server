# -*- coding: utf-8 -*-

from django.conf.urls.defaults import patterns, include
from django.contrib import admin
import os.path
from django.conf import settings
from jsonrpc import jsonrpc_site

# include views for JSON-RPC
import dailyreport.authentication.views
import dailyreport.company_object.views
import dailyreport.dataset.views
import dailyreport.reporting.views
import dailyreport.user_profile.views
import dailyreport.consumption.views
import dailyreport.deviation.views

admin.autodiscover()

URL_PREFIX = ''
if not settings.PRODUCTION_VERSION == True:
    URL_PREFIX = "dailyreport/"
    
    
PROJECT_PATH = os.path.dirname( __file__)

"""
reporting/json/ - URLs for json format data exchange

reporting/json/<reportId>/...

reporting/user/ - URLs for user-related data requests

reporting/import/ - 

reporting/html/<reportId>/... - HTML reports

"""

urlpatterns = patterns('',
    (r'^%sping/$' % URL_PREFIX, 'dailyreport.reporting.views.ping'),

    (r'^%sclient/(?P<path>.*)$' % URL_PREFIX, 'django.views.static.serve',
        {'document_root': os.path.join(PROJECT_PATH,'client').replace('\\','/')}),

    # Is a temporary bang
    (r'^%s$' % URL_PREFIX, 'dailyreport.reporting.views.index'),
    (r'^%sreporting/$' % URL_PREFIX, 'dailyreport.reporting.views.index'),
   
    # admin area
    (r'^%sadmin/' % URL_PREFIX, include(admin.site.urls)),
    
    #import company structure
    #(r'^%sreporting/import/' % URL_PREFIX , 'dailyreport.reporting.views.importData'),
    #import users
    #(r'^%sreporting/importusers/' % URL_PREFIX , 'dailyreport.reporting.views.importUsers'),
    
    # html report
    (r'^%sreporting/composite/$' % URL_PREFIX,
            'dailyreport.reporting.views.consumption'),
    
    (r'^%sreporting/report/(?P<output_format>\w+)/$' % URL_PREFIX,
            'dailyreport.reporting.views.open_report'),
    
    (r'^%sreporting/deviation_report/$' % URL_PREFIX,
            'dailyreport.reporting.views.deviation_report'),
                       
    (r'^%sreporting/electro/(?P<year>.*)/(?P<month>.*)/$' % URL_PREFIX,
            'dailyreport.reporting.views.electro'),
    
    # json rpc handler
    (r'^%sservice/$' % URL_PREFIX, jsonrpc_site.dispatch)
)