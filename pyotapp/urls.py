'''
Copyright (C) 2012,2013 Scuola Superiore Sant'Anna (http://www.sssup.it) 
and Consorzio Nazionale Interuniversitario per le Telecomunicazioni 
(http://www.cnit.it).

This file is part of PyoT, an IoT Django-based Macroprogramming Environment.

PyoT is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
  
PyoT is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
 
You should have received a copy of the GNU General Public License
along with PyoT.  If not, see <http://www.gnu.org/licenses/>.

@author: Andrea Azzara' <a.azzara@sssup.it>
'''
from django.conf.urls import patterns, include, url
from pyot.Forms import CustomRegistrationForm
#from registration.backends.default.views import RegistrationView
#import registration.backends.default.urls as regUrls

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()
import pyot.regbackend
from pyot.views import *

urlpatterns = patterns('',
    url(r'^$', home, name='home'),
    url(r'^settings/', pyot.views.settings, name='settings'),
    url(r'^startServer/(?P<wid>\d*)', pyot.views.startServer),
    url(r'^stopServer/(?P<wid>\d*)', pyot.views.stopServer),
    url(r'^getServerStatus', pyot.views.getServerStatus),
    url(r'^hostsList', pyot.views.hostsList, name='hostsList'),
    url(r'^hosts', pyot.views.hosts, name='hosts'),
    url(r'^resources', pyot.views.resources, name='resources'),
    url(r'^connectivity', pyot.views.pingPage, name='connectivity'),
    url(r'^resourceList', pyot.views.resourceList),
    url(r'^resource/(?P<rid>\d*)', pyot.views.resourcePage),
    url(r'^resourceStatus/(?P<rid>\d*)', pyot.views.resourceStatus),
    url(r'^opRes', pyot.views.opRes),
    url(r'^observe', pyot.views.observe),
    url(r'^obsList', pyot.views.obsList),
    url(r'^obsLast/(?P<rid>\d*)/', pyot.views.obsLast),
    url(r'^subList/(?P<rid>\d*)/', pyot.views.subList),
    url(r'^remHandler/(?P<hid>\d*)/', pyot.views.remHandler),
    url(r'^cancelSub/', pyot.views.cancelSub),
    url(r'^handlers/', pyot.views.handlers, name='handlers'),
    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    url(r'^startPing/(?P<hid>\d*)', pyot.views.startPing),
    #url(r'^accounts/register/$', RegistrationView.as_view(form_class=CustomRegistrationForm), {'backend': 'registration.backends.default.DefaultBackend','form_class': CustomRegistrationForm}, name='registration_register'),
    #(r'^accounts/', include('registration.backends.default.urls')), 
    url(r'^', include('django.contrib.auth.urls')),    
    url(r'^login/$', 'django.contrib.auth.views.login',name="my_login"),
    url(r'^myaccount', 'pyot.views.myaccount', name='myaccount'), 
    url(r'^deleteUser', 'pyot.views.deleteUser', name='deleteuser'), 
    url(r'^confirmDelete', 'pyot.views.confirmDeleteUser', name='confirmdeleteuser'), 
    url(r'^contacts', 'pyot.views.contacts', name='contacts'), 
)

import os, settings
urlpatterns += patterns('',
            url(r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_ROOT}),
    )
urlpatterns += patterns('',
            url(r'^media/(?P<path>.*)$', 'django.views.static.serve',{'document_root': settings.MEDIA_ROOT, 'show_indexes': True}),
            )

