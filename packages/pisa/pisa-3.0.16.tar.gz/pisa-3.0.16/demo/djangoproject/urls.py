from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^$', 'djangoproject.views.index'),
    (r'^download', 'djangoproject.views.download'),
)
