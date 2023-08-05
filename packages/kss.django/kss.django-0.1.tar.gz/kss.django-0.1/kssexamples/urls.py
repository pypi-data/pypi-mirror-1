from django.conf.urls.defaults import patterns, include, handler404
from django.conf import settings

from kssexamples.views import time_of_day
from kssexamples import ajax

handler404 # Pyflakes

urlpatterns = patterns(
    '',
    (r'^admin/', include('django.contrib.admin.urls')),
    (r'^kss/', include('kss.django.urls')),
    (r'^time_of_day', time_of_day),
    (r'ajax/time_of_day', ajax.time_of_day),
)

if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^media/(?P<path>.*)$', 'django.views.static.serve', 
         {'document_root': settings.MEDIA_ROOT}),
    )
