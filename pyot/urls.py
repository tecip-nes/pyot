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
from django.contrib import admin

from pyot import views
import settings


# Uncomment the next two lines to enable the admin:
admin.autodiscover()

urlpatterns = patterns(
    '',
    url(r'^$', views.home, name='home'),
    url(r'^settings/', views.settings, name='settings'),
    url(r'^startServer/(?P<wid>\d*)', views.startServer),
    url(r'^stopServer/(?P<wid>\d*)', views.stopServer),
    url(r'^getServerStatus', views.getServerStatus),
    url(r'^hostsList', views.hostsList, name='hostsList'),
    url(r'^hosts', views.hosts, name='hosts'),
    url(r'^resources', views.resources, name='resources'),
    url(r'^connectivity', views.pingPage, name='connectivity'),
    url(r'^resourceList', views.resourceList),
    url(r'^resource/(?P<rid>\d*)', views.resourcePage),
    url(r'^resourceStatus/(?P<rid>\d*)', views.resourceStatus),
    url(r'^opRes', views.opRes),
    url(r'^observe', views.observe),
    url(r'^obsList', views.obsList),
    url(r'^obsLast/(?P<rid>\d*)/', views.obsLast),
    url(r'^subList/(?P<rid>\d*)/', views.subList),
    url(r'^remHandler/(?P<hid>\d*)/', views.remHandler),
    url(r'^cancelSub/', views.cancelSub),
    url(r'^handlers/', views.handlers, name='handlers'),
    url(r'^startPing/(?P<hid>\d*)', views.startPing),
    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    url(r'^', include('django.contrib.auth.urls')),
)

urlpatterns += patterns(
    '',
    url(r'^static/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': settings.STATIC_ROOT}),
)
urlpatterns += patterns(
    '',
    url(
        r'^media/(?P<path>.*)$',
        'django.views.static.serve',
        {'document_root': settings.MEDIA_ROOT, 'show_indexes': True}
    ),
)
