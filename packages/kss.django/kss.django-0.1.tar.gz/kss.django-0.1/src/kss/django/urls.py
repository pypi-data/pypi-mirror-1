from django.conf.urls.defaults import patterns, url
from kss.django.views import kss_js, extra_js

urlpatterns = patterns(
    '',
    url(r'^kss.js$', kss_js, name='kss.js'),
    url(r'^(?P<js_name>[-\w]+.js)$', extra_js, name='kss_extra_scripts'))
