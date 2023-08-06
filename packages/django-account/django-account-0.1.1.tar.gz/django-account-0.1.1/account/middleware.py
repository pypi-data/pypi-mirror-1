"""
This module contains middlewares for account application:
    * DebugLoginMiddleware
    * OneTimeCodeAuthMiddleware
    * TestCookieMiddleware
"""

from django.http import HttpResponseRedirect
from django.contrib.auth import login, authenticate
from django.conf import settings

from account.util import email_template, str_to_class
from account.auth_key import decode_key, InvalidKey
from account import settings as app_settings
from account.views import message, render_to

UserModel = str_to_class(app_settings.USER_MODEL)

def login_user(request, user):
    user.backend = 'django.contrib.auth.backends.ModelBackend'
    login(request, user)    


class DebugLoginMiddleware(object):
    """
    This middleware authenticates user with just an
    ID parameter in the URL.
    This is dangerous middleware, use it with caution.
    """

    def process_request(self, request):
        """
        Login user with ID from loginas param of the query GET data.

        Do it only then settings.ACCOUNT_LOGIN_DEBUG is True
        """

        if getattr(settings, 'ACCOUNT_LOGIN_DEBUG', False):
            try:
                id = int(request.GET.get('loginas', 0))
                user = UserModel.objects.get(pk=id)
            except ValueError:
                return
            except UserModel.DoesNotExist:
                return
            else:
                login_user(user)


class AuthKeyMiddleware(object):
    """
    This middleware can authenticate user with auth key in HTTP request.
    """

    def process_request(self, request):

        key = request.REQUEST.get('authkey', None)
        
        try:
            args = decode_key(key)
        except InvalidKey:
            return None

        try:
            user = UserModel.objects.get(pk=args['uid'])
        except UserModel.DoesNotExist:
            return

        action = args.get('action')
        if 'activation' == action:
            if not user.is_active:
                user.is_active = True
                user.save()
                email_template(user.email, 'account/mail/welcome',
                               user=user, domain=app_settings.get_domain())
                login_user(request, user)

        if user.is_active:
            # TODO: WTF does that commented block mean? Kill it!
            # NOT USED: reset_password_email indicates that request has been made via link from email
            # reset_password is used for signing request from web form
            if 'reset_password' == action:
                pass
                #user.set_password(args['password'])
                #user.save()
                #return message(request, _('Password have been changed. You can log in now.'))

            if 'new_email' == action:
                if 'email' in args:
                    user.email = args['email']
                    user.save()
                    login_user(request, user)

            if 'login' == action:
                login_user(request, user)
                

# TODO: Delete?
#class TestCookieMiddleware(object):
    #"""
    #This middleware fixes error that appeares when user try to login
    #not from page that was generated with django.contrib.auth.views.login view.
    #"""

    #def process_view(self, request, view_func, view_args, view_kwargs):
        #"""
        #Setup test cookie.
        #"""

        #request.session.set_test_cookie()
