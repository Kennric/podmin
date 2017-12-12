# django stuff
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, get_object_or_404
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.conf import settings
from django.core.files import File
from django.core.servers.basehttp import FileWrapper
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.template import RequestContext

# podmin app stuff
from podmin.models import Podcast, Episode
from podmin.forms import PodcastForm, EpisodeForm

# python stuff
import time
import logging
import os

logger = logging.getLogger(__name__)

def user_role_check(req, slug):
    """
    Check what roles the user has relative to a particular podcast
    """
    user = req.user

    manager = user.groups.filter(name="%s_managers" % slug).exists()
    editor = user.groups.filter(name="%s_editors" % slug).exists()
    webmaster = user.groups.filter(name="%s_webmasters" % slug).exists()

    return (user, manager, editor, webmaster)

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
    form_class = RegistrationForm

    if request.method == 'POST':
        form = form_class(data=request.POST)

        if form.is_valid():
            contact_name = request.POST.get(
                'contact_name'
            , '')
            contact_email = request.POST.get(
                'contact_email'
            , '')
            form_content = request.POST.get('content', '')

            # Email the profile with the
            # contact information
            template = get_template('contact_template.txt')
            context = Context({
                'contact_name': contact_name,
                'contact_email': contact_email,
                'form_content': form_content,
            })
            content = template.render(context)
            email = EmailMessage(
                "New contact form submission",
                content,
                "Your website" +'',
                ['youremail@gmail.com'],
                headers = {'Reply-To': contact_email }
            )
            email.send()
            return redirect('contact')

    return render(request, 'contact.html', {'form': form_class,})
