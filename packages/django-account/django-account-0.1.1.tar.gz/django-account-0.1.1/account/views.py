# -*- coding: utf-8
from datetime import datetime, timedelta

from django.conf import settings
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.contrib import auth
from django.utils.translation import ugettext as _, string_concat
from django.http import HttpResponseRedirect

from account.forms import ResetPasswordForm,\
                          ChangePasswordForm, LoginForm, NewEmailForm
from account.util import email_template, build_redirect_url, render_to, str_to_class
from account.auth_key import wrap_url, decode_key, InvalidKey
from account import settings as app_settings

RegistrationForm = str_to_class(app_settings.REGISTRATION_FORM)
LoginForm = str_to_class(app_settings.LOGIN_FORM)
ResetPasswordForm = str_to_class(app_settings.RESET_PASSWORD_FORM)
ChangePasswordForm = str_to_class(app_settings.CHANGE_PASSWORD_FORM)

UserModel = str_to_class(app_settings.USER_MODEL)
if app_settings.REGISTRATION_CALLBACK:
    registration_callback = str_to_class(app_settings.REGISTRATION_CALLBACK)
else:
    registration_callback = None

@render_to('account/message.html')
def message(request, msg):
    """
    Shortcut that prepare data for message view.
    """

    return {'message': msg}


@render_to('account/registration.html')
def registration(request, form_class=RegistrationForm):
    if request.user.is_authenticated():
        return message(request, _('You have to logout before registration'))
    if not app_settings.REGISTRATION:
        return message(request, _('Sorry. Registration is disabled.'))

    if 'POST' == request.method:
        form = form_class(request.POST, request.FILES)
    else:
        form = form_class()

    if form.is_valid():
        user = form.save()
        if registration_callback:
            registration_callback(request, user)
        password = form.cleaned_data['password']
        if app_settings.ACTIVATION:
            user.is_active = False
            user.save()
            url = 'http://%s%s' % (app_settings.get_domain(), reverse('registration_complete'))
            url = wrap_url(url, uid=user.id, action='activation')
            params = {'domain': app_settings.get_domain(), 'login': user.username, 'url': url,
                      'password': password}
            if email_template(user.email, 'account/mail/registration', **params):
                return HttpResponseRedirect(reverse('account_created'))
            else:
                user.delete()
                return message(request, _('The error was occuried while sending email with activation code. Account was not created. Please, try later.'))
        else:
            user.backend = 'django.contrib.auth.backends.ModelBackend'
            auth.login(request, user)    
            args = {'domain': app_settings.get_domain(), 'user': user, 'password': password}
            email_template(user.email, 'account/mail/welcome', **args)
            return HttpResponseRedirect(app_settings.REGISTRATION_REDIRECT_URL())
    return {'form': form,
            }


@render_to('account/reset_password.html')
def reset_password(request, form_class=ResetPasswordForm):
    if 'POST' == request.method:
        form = form_class(request.POST)
    else:
        form = form_class()

    if form.is_valid():
        user = UserModel.objects.get(email=form.cleaned_data['email'])
        url = 'http://%s%s' % (app_settings.get_domain(), reverse('auth_password_change'))

        url = wrap_url(url, uid=user.id)
        args = {'domain': app_settings.get_domain(), 'url': url, 'user': user}
        if email_template(user.email, 'account/mail/reset_password', **args):
            return message(request, _('Check the mail please'))
        else:
            return message(request, _('Unfortunately we could not send you email in current time. Please, try later'))
    return {'form': form}


@render_to('account/login.html')
def login(request, form_class=LoginForm):
    if request.user.is_authenticated():
        return message(request, _('You are already authenticated'))

    if 'POST' == request.method:
        form = form_class(request.POST, request=request)
    else:
        form = form_class(request=request)

    request.session['login_redirect_url'] = request.GET.get('next')
    if form.is_valid():
        redirect_url = build_redirect_url(request, settings.LOGIN_REDIRECT_URL)
        return HttpResponseRedirect(redirect_url)
    return {'form': form,
            }


@render_to('account/new_password.html')
def new_password(request):
    if not request.user.is_authenticated():
        key = request.REQUEST.get('authkey', None)
        try:
            args = decode_key(key)
        except InvalidKey:
            return HttpResponseRedirect(reverse('auth_login') + '?next=%s' % request.path)
        uid = args['uid']
    else:
        key = ''
        uid = request.user.id

    require_old = not bool(key)
    if 'POST' == request.method:
        form = ChangePasswordForm(request.POST, require_old=require_old)
    else:
        form = ChangePasswordForm(require_old=require_old, initial={'authkey': key, 'uid': uid})

    if form.is_valid():
        form.save()
        return HttpResponseRedirect(reverse('auth_password_changed')) 
    return {'form': form}


@login_required
@render_to('account/change_email.html')
def change_email(request):
    if 'POST' == request.method:
        form = NewEmailForm(request.POST)
    else:
        form = NewEmailForm()

    if form.is_valid():
        email = form.cleaned_data['email']
        url = 'http://%s%s' % (app_settings.get_domain(), reverse('auth_email_changed'))
        url = wrap_url(url, uid=request.user.id, action='new_email', email=email)
        args = {'domain': app_settings.get_domain(), 'url': url, 'email': email,}
        if email_template(email, 'account/mail/new_email', **args):
            return message(request, _('Check the mail please'))
        else:
            return message(request, _('Unfortunately we could not send you email in current time. Please, try later'))
    return {'form': form}


@login_required
def email_changed(request):
    return message(request, _('Your email has been changed to %s') % request.user.email)


@render_to('account/password_changed.html')
def password_changed(request):
    return {'login_url': reverse('auth_login'),
            }


def logout(request):
    auth.logout(request)
    next = request.GET.get('next', reverse('auth_logout_successful'))
    return HttpResponseRedirect(next)


def logout_successful(request):
    return message(request, _('You have successfully loged out'))
