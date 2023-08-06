from django.conf.urls.defaults import *
import django.contrib.auth.views
from django.views.generic.simple import direct_to_template
from django.contrib.auth.decorators import login_required

from account import views

# Note that url names are the same as in django-registration application

urlpatterns = patterns('',
    url(r'^registration/$', views.registration, name='registration_register'),
    url(r'^login/$', views.login, name='auth_login'),
    url(r'^logout/$', views.logout, name='auth_logout'),
    url(r'^logout/successful/$', views.logout_successful, name='auth_logout_successful'),
    url(r'^password/reset/$', views.reset_password,
        name='auth_password_reset'),
    url(r'^password/change/$', views.new_password, name='auth_password_change'),
    url(r'^password/changed/$', views.password_changed, name='auth_password_changed'),
    url(r'^created/$', direct_to_template, {'template':'account/created.html'},
        name='account_created'),
    url(r'^welcome/$', direct_to_template, {'template':'account/welcome.html'},
        name='registration_complete'),
    url(r'^email/change/$', views.change_email, name='auth_email_change'),
    url(r'^email/changed/$', views.email_changed, name='auth_email_changed'),
)
