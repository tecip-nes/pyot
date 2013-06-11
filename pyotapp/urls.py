'''
@author: Andrea Azzara' <a.azzara@sssup.it>
'''
from django.conf.urls.defaults import patterns, include, url
from pyot.Forms import CustomRegistrationForm
from registration.views import register
import registration.backends.default.urls as regUrls
from django.views.generic.simple import direct_to_template

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()
import pyot.regbackend
from pyot.views import *

urlpatterns = patterns('',
    url(r'^$', home, name='home'),
    url(r'^settings/', pyot.views.settings, name='settings'),
    url(r'^startServer', pyot.views.startServer),
    url(r'^stopServer', pyot.views.stopServer),
    url(r'^getServerStatus', pyot.views.getServerStatus.as_view()),
    url(r'^hostsList', pyot.views.hostsList, name='hostsList'),
    url(r'^hosts', pyot.views.hosts, name='hosts'),
    url(r'^resources', pyot.views.resources, name='resources'),
    url(r'^connectivity', pyot.views.pingPage, name='connectivity'),
    url(r'^resourceList', pyot.views.resourceList),
    url(r'^pushUpdate/(?P<className>[A-Za-z]+)', pyot.views.pushUpdate.as_view()), 
    url(r'^resource/(?P<rid>\d*)', pyot.views.resourcePage),
    url(r'^resourceStatus/(?P<rid>\d*)', pyot.views.resourceStatus.as_view()),
    url(r'^opRes', pyot.views.opRes),
    url(r'^observe', pyot.views.observe),
    url(r'^obsList', pyot.views.obsList),
    url(r'^obsLast/(?P<rid>\d*)/', pyot.views.obsLast.as_view()),
    url(r'^subList/(?P<rid>\d*)/', pyot.views.subList),
    url(r'^remHandler/(?P<hid>\d*)/', pyot.views.remHandler),
    url(r'^terminate/', pyot.views.terminate),
    #url(r'^scriptUp/(?P<rid>\d*)/', 'pyot.views.scriptUp', name='uploadScript'),
    #url(r'^getScriptCode/', 'pyot.views.getScriptCode'),
    #url(r'^loadScriptCode/', 'pyot.views.loadScriptCode'),
    #url(r'^reqVmMeta/', 'pyot.views.reqVmMeta'),
    url(r'^handlers/', pyot.views.handlers, name='handlers'),
    #url(r'^sendScriptToRes/(?P<rid>\d*)/(?P<sid>\d*)/', 'pyot.views.SendScriptCode'),
    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    #url(r'^settings/', include('livesettings.urls')),
    url(r'^startPing/(?P<hid>\d*)', pyot.views.startPing),
    url(r'^shutdown', pyot.views.shutdown),  
    url(r'^accounts/register/$', 'registration.views.register', {'backend': 'registration.backends.default.DefaultBackend','form_class': CustomRegistrationForm}, name='registration_register'),
    #(r'^accounts/', include(regUrls)),
    #(r'^accounts/register/$', 'registration.views.register', {'form_class' : CustomRegistrationForm, 'backend': 'registration.backends.default.DefaultBackend'}),
    (r'^accounts/', include('registration.backends.default.urls')), 
    url(r'^', include('django.contrib.auth.urls')),    
    url(r'^login/$', 'django.contrib.auth.views.login',name="my_login"),
    #url(r'^cam', 'pyot.views.cam', name='cam'),  
    url(r'^myaccount', 'pyot.views.myaccount', name='myaccount'), 
    url(r'^deleteUser', 'pyot.views.deleteUser', name='deleteuser'), 
    url(r'^confirmDelete', 'pyot.views.confirmDeleteUser', name='confirmdeleteuser'), 
    url(r'^contacts', 'pyot.views.contacts', name='contacts'), 
    ('^thanks/$', direct_to_template, {'template': 'thanks.htm'})
)

import os, settings
urlpatterns += patterns('',
            url(r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_ROOT}),
    )

