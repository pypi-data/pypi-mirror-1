from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^test/$', 'views.display'),
    (r'^test/asc/(\d+)/$', 'views.sortAsc'),
    (r'^test/desc/(\d+)/$', 'views.sortDesc'),
)
