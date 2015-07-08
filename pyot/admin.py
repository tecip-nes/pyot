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

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from pyot.models import *


#from django.contrib.auth.models import User
#from pyot.models import UserProfile

admin.site.register(Host)
admin.site.register(Resource)
admin.site.register(EventHandler)
admin.site.register(Subscription)
admin.site.register(CoapMsg)
admin.site.register(Network)
admin.site.register(Log)
admin.site.register(UserProfile)
admin.site.register(TResProcessing)
admin.site.register(TResT)
admin.site.register(RplGraph)
admin.site.register(EmulatorState)
admin.site.register(pyMapReduce)
admin.site.register(pyMap)


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'profile'


class UserAdmin(UserAdmin):
    inlines = (UserProfileInline, )

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
