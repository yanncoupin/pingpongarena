from django.conf.urls.defaults import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^$',      'client.views.home', name='home'),
    url(r'^newgame$', 'client.views.newgame', name='newgame'),
    url(r'^game/(?P<game_id>\d+)$', 'client.views.game', name='game'),
    url(r'^update$', 'client.views.update', name='update'),
    # url(r'^pingpongarena/', include('pingpongarena.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)
