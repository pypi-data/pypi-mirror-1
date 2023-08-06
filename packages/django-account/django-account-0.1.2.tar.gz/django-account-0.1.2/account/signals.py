from django.contrib import auth
from django.dispatch import Signal
from django.contrib.sites.models import Site

from urlauth.signals import key_loaded, key_processed

from account.util import email_template


account_created = Signal(providing_args=['user'])


def login_user(request, user):
    user.backend = 'django.contrib.auth.backends.ModelBackend'
    auth.login(request, user)


def key_loaded_handler(key, request):
    extra = key.export_data()
    action = extr.get('action')
    user = request.user

    if 'activation' == action:
        if not user.is_active:
            user.is_active = True
            user.save()
            email_template(user.email, 'account/mail/welcome',
                           user=user, domain=Site.objects.get_current().domain)

    if user.is_active:
        if 'new_email' == action:
            if 'email' in extra:
                user.email = args['email']
                user.save()
