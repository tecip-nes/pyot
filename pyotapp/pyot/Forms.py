from django import forms
#import os
#import logging
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

'''
class ScriptForm(forms.Form):
    docfile = forms.FileField(
        label='Select a file',
        help_text='must be a .py file'
    )
    maj_v = forms.CharField(widget=forms.TextInput(attrs={'size':'1'}),
                              max_length=1, required=True)
    min_v = forms.CharField(widget=forms.TextInput(attrs={'size':'1'}),
                              max_length=1, required=True)
    def clean(self):
        cleaned_data = self.cleaned_data
        #TODO: controllo del numero di telefono e del prefisso
        #check passwords match
        f = cleaned_data.get("docfile")
        _name, ext = os.path.splitext(f.name)
        if ext != '.py' :
            logging.debug('estensione errata: ' + ext)
            raise forms.ValidationError("Must be a .py file")
        return cleaned_data 
''' 
class HandlerForm(forms.Form):
    Description = forms.CharField(widget=forms.TextInput(attrs={'size':'30'}), max_length=50, required=True)
    MaxActivations = forms.IntegerField(min_value = 1, initial=1)

'''    
class CodeHandlerForm(HandlerForm):
    VmResource = forms.ModelChoiceField(queryset = VmResource.objects.filter(host__active=True) )
    Script = forms.ModelChoiceField(queryset = PyScript.objects.all() )
'''
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


