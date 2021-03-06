# django stuff
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.contrib.auth import authenticate, login, logout
from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import get_template
from django.contrib.auth.models import User

# podmin app stuff
from podmin.forms import RegistrationForm

# python stuff
import logging

logger = logging.getLogger(__name__)


def login_user(request):
    """
    Log a user in, or display the login form
    """
    state = "Please log in."
    username = password = ''
    if request.POST:
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                if request.POST.get('next'):
                    return HttpResponseRedirect(request.POST.get('next'))
                else:
                    return HttpResponseRedirect('/')
            else:
                state = "Your account is not active."
        else:
            next = request.POST.get('next')
            state = "Invalid username or password."
    else:
        next = request.GET.get('next')

    if request.GET.get('logout', False):
        state = "Logged out successfully!"

    if request.user.is_authenticated():
        return HttpResponseRedirect(next)

    return render(request, 'registration/login.html', {
        'state': state, 'username': username, 'next': next, 'title': 'Log In'})


def logout_user(request):
    """
    Log a user out
    """
    logout(request)
    return HttpResponseRedirect('{}?logout=true'.format(reverse('login')))


def podcast_request(request):
    form = RegistrationForm()
    if request.method == 'POST':
        form = RegistrationForm(data=request.POST)

        if form.is_valid():
            name = request.POST.get('name', '')
            email = request.POST.get('email', '')
            username = request.POST.get('username', '')
            podcast_name = request.POST.get('podcast_name', '')
            description = request.POST.get('description', '')
            notes = request.POST.get('notes', '')

            # Email the profile with the
            # contact information
            template = get_template('podmin/site/request_email.txt')
            context = {
                'name': name,
                'username': username,
                'email': email,
                'podcast_name': podcast_name,
                'description': description,
                'notes': notes
            }
            subject = "New Podcast Request"
            body = template.render(context)
            from_address = settings.EMAIL_FROM

            to_addresses = [x[0] for x in User.objects.filter(
                groups__name__in=['admins']).values_list('email')]

            if to_addresses:
                email = EmailMessage(
                    subject,
                    body,
                    from_address,
                    to_addresses,
                    headers={'Reply-To': email}
                )
                email.send()
                messages.success(request,
                                 'Thank you, your request was submitted.')
                return HttpResponseRedirect('/')
            else:
                messages.warning(request, 'No one to send email to!')

    return render(request, 'podmin/site/request_podcast.html', {'form': form})
