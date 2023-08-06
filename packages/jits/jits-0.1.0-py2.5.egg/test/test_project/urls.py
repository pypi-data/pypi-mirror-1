from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^$', 'test_app.views.index'),
)
