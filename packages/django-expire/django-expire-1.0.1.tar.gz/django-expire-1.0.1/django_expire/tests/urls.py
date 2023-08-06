from django.conf.urls.defaults import patterns

urlpatterns = patterns('django_expire.tests.views',
    (r'^$', 'show_username'),
)
