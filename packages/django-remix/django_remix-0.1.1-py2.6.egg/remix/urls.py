from django.conf.urls.defaults import *

urlpatterns = patterns(
    '',
    (r'dashboard/(.*)', 'remix.views.dashboard'),
)
