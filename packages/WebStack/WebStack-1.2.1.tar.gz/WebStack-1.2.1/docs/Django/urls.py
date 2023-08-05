from django.conf.urls.defaults import *

# The groups defined by ?P<vp> (ie. having the name "vp") define the virtual
# path info for each resource. Modifications to the regular expressions used
# below should be accompanied by modifications in the handler code in
# examples/Django.

urlpatterns = patterns('',
    (r'^django/webstack/auth(?P<vp>/.*)?', 'djangoinstance.webstack.authapp.auth'),
    (r'^django/webstack/calendar(?P<vp>/.*)?', 'djangoinstance.webstack.calendarapp.calendar'),
    (r'^django/webstack/cookies(?P<vp>/.*)?', 'djangoinstance.webstack.cookiesapp.cookies'),
    (r'^django/webstack/form(?P<vp>/.*)?', 'djangoinstance.webstack.formapp.form'),
    (r'^django/webstack/login(?P<vp>/.*)?', 'djangoinstance.webstack.loginapp.login'),
    (r'^django/webstack/sessions(?P<vp>/.*)?', 'djangoinstance.webstack.sessionsapp.sessions'),
    (r'^django/webstack/simplewithlogin(?P<vp>/.*)?', 'djangoinstance.webstack.simplewithloginapp.simplewithlogin'),
    (r'^django/webstack/simple(?P<vp>/.*)?', 'djangoinstance.webstack.simpleapp.simple'),
    (r'^django/webstack/unicode(?P<vp>/.*)?', 'djangoinstance.webstack.unicodeapp.unicode'),
    (r'^django/webstack/verysimple(?P<vp>/.*)?', 'djangoinstance.webstack.verysimpleapp.verysimple'),
)
