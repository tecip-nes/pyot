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
import Forms
from models import UserProfile
from django.contrib.auth import login

def user_created(sender, user, request, **kwargs):
    form = Forms.CustomRegistrationForm(request.POST)
    profile = UserProfile.objects.get(user=user)
    profile.organization= form.data['organization']
    user.first_name = form.data['first_name']
    user.last_name = form.data['last_name']
    user.save()
    profile.save()

def login_on_activation(sender, user, request, **kwargs):
    user.backend='django.contrib.auth.backends.ModelBackend' 
    login(request,user)

from registration.signals import user_registered, user_activated
user_registered.connect(user_created)
user_activated.connect(login_on_activation)
