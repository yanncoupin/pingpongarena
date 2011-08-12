from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('',
    url(r'^$', 'client.views.home', name='home'),
    url(r'^newgame$', 'client.views.newgame', name='newgame'),
    url(r'^game/(?P<game_id>\d+)$', 'client.views.game', name='game'),
    url(r'^update$', 'client.views.update', name='update'),
    url(r'^login$', 'django.contrib.auth.views.login', name='login'),
)
