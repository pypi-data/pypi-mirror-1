from django.conf import settings
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

_domain = None

def get_domain():
    global _domain

    if _domain is None:
        try:
            _domain = settings.ACCOUNT_DOMAIN
        except AttributeError:
            try:
                from django.contrib.sites.models import Site
            except ImportError:
                _domain = 'not.defined.com'
            else:
                _domain = Site.objects.get_current().domain
    return _domain


USER_MODEL = getattr(settings, 'ACCOUNT_USER_MODEL', 'django.contrib.auth.models.User')
AUTH_KEY_TIMEOUT = getattr(settings, 'ACCOUNT_AUTH_KEY_TIMEOUT', 60 * 60 * 24)
REGISTRATION_REDIRECT_URL = lambda: getattr(settings, 'ACCOUNT_REGISTRATION_REDIRECT_URL',
    reverse('registration_complete'))

REGISTRATION_FORM = getattr(settings,
    'ACCOUNT_REGISTRATION_FORM', 'account.forms.RegistrationForm')
LOGIN_FORM = getattr(settings,
    'ACCOUNT_LOGIN_FORM', 'account.forms.LoginForm')
RESET_PASSWORD_FORM = getattr(settings,
    'ACCOUNT_RESET_PASSWORD_FORM', 'account.forms.ResetPasswordForm')
CHANGE_PASSWORD_FORM = getattr(settings,
    'ACCOUNT_CHANGE_PASSWORD_FORM', 'account.forms.ChangePasswordForm')
PASSWORD_CHANGE_REQUIRES_OLD = getattr(settings,
    'ACCOUNT_PASSWORD_CHANGE_REQUIRES_OLD', True)
CAPTCHA = getattr(settings, 'ACCOUNT_CAPTCHA', False)
CAPTCHA_FIELD = getattr(settings, 'ACCOUNT_CAPTCHA_FIELD', 'captcha.fields.CaptchaField')
CAPTCHA_LABEL = getattr(settings, 'ACCOUNT_CAPTCHA_LABEL', _('Enter the text in the image'))

REGISTRATION = getattr(settings, 'ACCOUNT_REGISTRATION', True)
ACTIVATION = getattr(settings, 'ACCOUNT_ACTIVATION', True)
REGISTRATION_CALLBACK = getattr(settings, 'ACCOUNT_REGISTRATION_CALLBACK', None)
AGREEMENT = getattr(settings, 'ACCOUNT_AGREEMENT', False)

if AGREEMENT:
    AGREEMENT_LINK = getattr(settings, 'ACCOUNT_AGREEMENT_LINK', '')
    AGREEMENT_TEXT = getattr(settings, 'ACCOUNT_AGREEMENT_TEXT',
        _('I accept user <a target="_blank" href="%s">agreement</a>'))
    if AGREEMENT_LINK:
        AGREEMENT_TEXT %= AGREEMENT_LINK
