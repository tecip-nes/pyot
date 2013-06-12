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
from django import forms
from models import Resource, METHOD_CHOICES
#from django.forms import ModelForm
from registration.forms import RegistrationFormTermsOfService
#, RegistrationForm
#from models import UserProfile
#from django.forms import *
#http://dmitko.ru/django-registration-form-custom-field/
'''
class UserProfileForm(forms.Form):
    organization = forms.CharField(widget=forms.TextInput(attrs={'size':'30'}),
                              max_length=30)
    #model = UserProfile
'''
#RegistrationFormTermsOfService.base_fields.update(UserProfileForm.base_fields)

class CustomRegistrationForm(RegistrationFormTermsOfService):
    first_name = forms.CharField()
    last_name = forms.CharField()
    organization = forms.CharField()
    '''
    def save(self, profile_callback=None):
        user = super(CustomRegistrationForm, self).save(profile_callback=None)
        #user.get_profile().organization=self.cleaned_data['organization']
        user.first_name='ahah'
        user.save()
        org = UserProfile.objects.get(user=user)
        org.organization='test'
        #self.cleaned_data['organization']
        org.save()
        #user.save()
    '''

class HandlerForm(forms.Form):
    Description = forms.CharField(widget=forms.TextInput(attrs={'size':'30'}), max_length=50, required=True)
    MaxActivations = forms.IntegerField(min_value = 1, initial=1)

class MsgHandlerForm(HandlerForm):
    Resource = forms.ModelChoiceField(queryset = Resource.objects.all().filter(host__active=True).exclude(uri='.well-known') )
    Payload = forms.CharField(widget=forms.TextInput(attrs={'size':'30'}),
                              max_length=30, required=False)
    Method = forms.CharField(max_length=5, widget=forms.Select(choices=METHOD_CHOICES))
    
class MsgHandlerFormFreq(MsgHandlerForm):  
    EventCount = forms.IntegerField(min_value = 1, initial=10, required=True)
    Seconds = forms.IntegerField(min_value = 1, initial=10, required=True)

class ContactForm(forms.Form):
    subject = forms.CharField(max_length=100)
    message = forms.CharField(widget=forms.Textarea)
    sender = forms.EmailField()


