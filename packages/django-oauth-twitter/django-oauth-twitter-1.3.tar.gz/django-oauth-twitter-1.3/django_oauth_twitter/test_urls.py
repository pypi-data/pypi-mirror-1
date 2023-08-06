from django.conf.urls.defaults import *

from django_oauth_twitter.views import OAuthTwitter

oauthtwitter = OAuthTwitter(signed_in_url='/home/')

def home(request):
    pass

urlpatterns = patterns('',
    url(r'^twitter/', include(oauthtwitter.urls)),
    url(r'^home/', home, name='home'),
    url(r'^logout/', 'django.contrib.auth.views.logout'),
)

