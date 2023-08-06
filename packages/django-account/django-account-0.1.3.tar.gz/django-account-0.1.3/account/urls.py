from django.conf.urls.defaults import *
import django.contrib.auth.views
from django.views.generic.simple import direct_to_template
from django.contrib.auth.decorators import login_required

from account import views

urlpatterns = patterns('',
    # Common functions
    url(r'^login/$', views.login, name='auth_login'),
    url(r'^logout/$', views.logout, name='auth_logout'),
    url(r'^logout/successful/$', views.logout_successful, name='auth_logout_successful'),

    # Registration
    url(r'^registration/$', views.registration, name='registration_register'),
    url(r'^activation/required/$', direct_to_template, {'template':'account/activation_required.html'}, name='activation_required'),
    url(r'^registration/complete/$', direct_to_template, {'template':'account/registration_complete.html'}, name='registration_complete'),

    # Work with password
    url(r'^password/reset/$', views.password_reset, name='auth_password_reset'),
    url(r'^password/change/$', views.password_change, name='auth_password_change'),
    url(r'^password/change/done/$', views.password_change_done, name='auth_password_change_done'),

    # Work with email
    url(r'^email/change/$', views.email_change, name='auth_email_change'),
    url(r'^email/change/done/$', views.email_change_done, name='auth_email_change_done'),
)
