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
from django.contrib.auth import logout
from django.core.mail import mail_admins
from django.http import HttpResponseRedirect
from django.shortcuts import render

from pyot.Forms import ContactForm


# @login_required
def myaccount(request):
    return render(request, 'account.html')


# @login_required
def deleteUser(request):
    return render(request, 'deleteuser.htm')

# @login_required
def confirmDeleteUser(request):
    request.user.delete()
    logout(request)
    return render(request, 'home.htm')


def contacts(request):
    if request.method == 'POST': # If the form has been submitted...
        form = ContactForm(request.POST) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']

            sender = form.cleaned_data['sender']
            mess = 'Sender is ' + sender + '\n' + message
            mail_admins(subject, mess, fail_silently=False, connection=None,
                        html_message=None)
            return HttpResponseRedirect('/thanks/') # Redirect after POST
    else:
        form = ContactForm() # An unbound form

    return render(request, 'contacts.htm', {
        'form': form,
    })

    return render(request, 'contacts.htm')

