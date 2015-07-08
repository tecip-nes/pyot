
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

from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save


TFMT = settings.TFMT
LOG_CHOICES = (
    (u'registration', u'registration'),
    (u'clean', u'clean'),
    (u'discovery', u'discovery'),
    (u'ghost', u'ghost'),
    (u'RdRetry', u'RdRetry'),
    (u'RdRec', u'RdRec'),
    (u'SubRec', u'SubRec'),
)


class UserProfile(models.Model):
    '''
    Custom user profile model including an 'organization' field.
    '''
    user = models.OneToOneField(User, unique=True, related_name='profile')
    organization = models.CharField(max_length=50, blank=False)

    def save(self, *args, **kwargs):
        try:
            existing = UserProfile.objects.get(user=self.user)
            self.id = existing.id # force update instead of insert
        except UserProfile.DoesNotExist:
            pass
        models.Model.save(self, *args, **kwargs)

    class Meta(object):
        app_label = 'pyot'


def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

post_save.connect(create_user_profile, sender=User)


class Log(models.Model):
    '''
    Defines a model to store several type of log messages in the db.
    '''
    log_type = models.CharField(max_length=30, choices=LOG_CHOICES)
    message = models.CharField(max_length=1024)
    timeadded = models.DateTimeField(auto_now_add=True, blank=True)

    def __unicode__(self):
        return u"{t} {log_type} {message}".format(log_type=self.log_type,
                                                  message=self.message,
                                                  t=self.timeadded.strftime(TFMT))

    class Meta(object):
        app_label = 'pyot'
