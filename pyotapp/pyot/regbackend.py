import Forms
from models import UserProfile
from django.contrib.auth import login
#, authenticate

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
