'''
Created on Oct 22, 2012

@author: Andrea Azzara' <a.azzara@sssup.it>
'''

from models import *
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
#from django.contrib.auth.models import User
#from pyot.models import UserProfile

admin.site.register(Host)
admin.site.register(Resource)
admin.site.register(EventHandler)
admin.site.register(Subscription)
admin.site.register(CoapMsg)
admin.site.register(RunningServer)
admin.site.register(Log)
admin.site.register(UserProfile)
admin.site.register(ModificationTrace)


# Define an inline admin descriptor for UserProfile model
# which acts a bit like a singleton
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'profile'

# Define a new User admin
class UserAdmin(UserAdmin):
    inlines = (UserProfileInline, )

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
